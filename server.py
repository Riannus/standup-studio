#!/usr/bin/env python3
"""Local Standup Studio server with durable SQLite storage."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import sqlite3
import sys
import threading
from contextlib import contextmanager
import webbrowser

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
ROOT = Path(getattr(sys, "_MEIPASS", APP_DIR))
def user_data_dir():
    override = os.environ.get("STANDUP_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "Stand-up Studio"
    if __import__("sys").platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Stand-up Studio"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "stand-up-studio"


DATA_DIR = user_data_dir()
DB = DATA_DIR / "standup.sqlite3"
LEGACY_DB = APP_DIR / "standup.sqlite3"
LEGACY_JSON = APP_DIR / "data.json"
PORT = int(os.environ.get("STANDUP_PORT", "8765"))


@contextmanager
def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DB.exists() and LEGACY_DB.exists():
        old = sqlite3.connect(LEGACY_DB, timeout=10)
        new = sqlite3.connect(DB, timeout=10)
        try:
            old.backup(new)
        finally:
            new.close()
            old.close()
    conn = sqlite3.connect(DB, timeout=10)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK (id = 1), payload TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initial_payload():
    if LEGACY_JSON.exists():
        try:
            data = json.loads(LEGACY_JSON.read_text(encoding="utf-8"))
            if isinstance(data.get("jokes"), list) and isinstance(data.get("scenario"), list):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return {"jokes": [], "scenario": []}


def read_payload():
    with connect() as conn:
        row = conn.execute("SELECT payload, updated_at FROM app_state WHERE id=1").fetchone()
        if row:
            return row[0], row[1]
        payload = json.dumps(initial_payload(), ensure_ascii=False)
        conn.execute("INSERT INTO app_state(id,payload) VALUES(1,?)", (payload,))
        row = conn.execute("SELECT payload, updated_at FROM app_state WHERE id=1").fetchone()
        return row[0], row[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in {"/standup.sqlite3", "/standup.sqlite3-wal", "/standup.sqlite3-shm", "/data.json"}:
            self.send_error(404)
            return
        if self.path == "/api/data":
            payload, updated_at = read_payload()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Data-Updated", updated_at)
            self.end_headers()
            self.wfile.write(payload.encode("utf-8"))
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/data":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("jokes"), list) or not isinstance(data.get("scenario"), list):
                raise ValueError("Invalid data shape")
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            with connect() as conn:
                conn.execute("INSERT INTO app_state(id,payload,updated_at) VALUES(1,?,CURRENT_TIMESTAMP) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, updated_at=CURRENT_TIMESTAMP", (payload,))
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_error(400, str(exc))


if __name__ == "__main__":
    url = f"http://127.0.0.1:{PORT}"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        print(f"Standup Studio nejde spustit na portu {PORT}: {exc}")
        print(f"Pokud už aplikace běží, otevři {url}. Jinak zavři program, který port používá, a spusť aplikaci znovu.")
        raise SystemExit(1)

    print(f"Standup Studio běží na {url}. Pro ukončení zavři toto okno nebo stiskni Ctrl+C.")
    threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStandup Studio se ukončuje.")
    finally:
        server.server_close()

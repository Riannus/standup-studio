#!/bin/sh
set -eu

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Chybí Python 3. Nainstaluj Python 3 a spusť tento soubor znovu." >&2
  exit 1
fi

exec python3 server.py

# Standup Studio

Jednoduchá lokální aplikace pro psaní stand-up scénářů a správu knihovny nápadů. Každý uživatel má data uložená na svém počítači.

## Rychlé spuštění

### 1. Nainstaluj Python 3

Aplikace používá pouze Python a jeho vestavěné knihovny. Nic dalšího se neinstaluje. Pokud Python 3 ještě nemáš, stáhni ho z [python.org](https://www.python.org/downloads/).

### 2. Naklonuj repozitář

Otevři Terminál (na Windows PowerShell) a spusť:

```sh
git clone https://github.com/Riannus/standup-studio.git
cd standup-studio
```

### 3. Spusť aplikaci

- **macOS a Linux:** v Terminálu spusť `./start.sh`. Na Macu můžeš také dvojkliknout na `Spustit.command`.
- **Windows:** dvojklikni na `start.bat`, případně ho spusť z PowerShellu.

Otevře se prohlížeč na `http://127.0.0.1:8765`. Nech otevřené okno Terminálu nebo příkazového řádku; aplikaci ukončíš jeho zavřením nebo stisknutím `Ctrl+C`. Při dalším spuštění použij stejný příkaz a uložená data se znovu načtou.

## Ukládání dat

Vtipy a scénáře se automaticky ukládají do jedné SQLite databáze. SQLite je součástí Pythonu, takže není potřeba nic instalovat ani nastavovat. Databáze je uložená mimo repozitář, a proto zůstane zachovaná při aktualizaci, novém klonování i smazání složky aplikace.

Umístění databáze:

- **macOS:** `~/Library/Application Support/Stand-up Studio/standup.sqlite3`
- **Windows:** `%APPDATA%\Stand-up Studio\standup.sqlite3`
- **Linux:** `~/.local/share/stand-up-studio/standup.sqlite3` (nebo pod `XDG_DATA_HOME`)

Každý počítač má vlastní databázi. Chceš-li databázi zazálohovat, ukonči aplikaci a zkopíruj uvedený soubor na bezpečné místo. Starší `standup.sqlite3` nebo `data.json` ve složce projektu se při spuštění automaticky převezme.

## Aktualizace aplikace

Ve složce projektu spusť `git pull` a potom aplikaci znovu spusť přes `./start.sh` nebo `start.bat`. Databáze zůstává na stejném místě.

## Import nápadů

V knihovně nápadů klikni na **Importovat** a vyber `.txt` nebo `.csv` soubor. V textovém souboru odděl jednotlivé nápady řádkem s `---`; nepovinný řádek s tagy začíná `[tag]`:

```text
Text prvního nápadu
[tag] rodina práce
---
Text druhého nápadu
[tag] cestování
```

U CSV je každý řádek jeden nápad. První sloupec obsahuje text a další sloupce mohou obsahovat tagy.

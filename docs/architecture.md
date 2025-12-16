# System Architecture

## Purpose
Parse CWA agriculture weather JSON (F-A0010-001), store regional daily temperatures into SQLite, and provide a Streamlit UI to browse the data.

## Components
- Data Ingest (`app.py`)
  - Reads JSON (default: repo-local `F-A0010-001.json`, override via `--json`).
  - Creates/updates SQLite (`data.db`, override via `--db`).
  - Idempotent upsert on `(location, date)`.
- Storage
  - SQLite file `data.db`.
  - Tables:
    - `locations(id, name UNIQUE)`
    - `daily_temperatures(id, location_id, date, max_temp_c, min_temp_c, UNIQUE(location_id, date))`
  - Index: `idx_daily_temperatures_loc_date` on (`location_id`, `date`).
- Presentation (`streamlit_app.py`)
  - Reads from SQLite (path configurable in UI).
  - Filter by location (All or a specific region).
  - Displays tabular results with counts.

## Data Flow
1) Input: F-A0010-001 JSON (UTF-8).  
2) Extract: `cwaopendata.resources.resource.data.agrWeatherForecasts.weatherForecasts.location`.  
3) For each location: insert into `locations` (ignore duplicates).  
4) Zip `MaxT.daily` and `MinT.daily` by date; insert/update into `daily_temperatures`.  
5) Streamlit reads SQLite and renders tables; user may switch DB path and filter location.

## Configuration
- CLI flags (ingest):
  - `--json <path>`: path to JSON input.
  - `--db <path>`: path to SQLite output.
- Streamlit UI:
  - Text input for DB path (default `data.db`).
  - Location select box (“全部” or specific).

## Reliability & Idempotency
- UNIQUE(location_id, date) + `INSERT OR REPLACE` prevents duplicates.
- Schema creation is guarded by `IF NOT EXISTS`.
- Foreign keys enabled via `PRAGMA foreign_keys = ON`.

## Extensibility
- Add more weather elements: extend schema (new columns/table) and ingest loop.
- Alternative storage: swap SQLite for Postgres by replacing connection layer.
- APIs: expose data via FastAPI/Flask using the same DB schema.

## Security & Data Handling
- No secrets required; only local file access.
- Input validation: file existence check before ingest; key checks raise explicit errors.
- Streamlit UI does not write; it only reads SQLite.

## Dependencies
- Python 3.10+ recommended.
- Packages: see `requirements.txt` (currently Streamlit; stdlib covers ingest/SQLite).

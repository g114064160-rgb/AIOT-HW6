## Overview
- Parse the CWA agriculture weather JSON file `F-A0010-001.json`.
- Extract each region’s daily highest/lowest temperatures.
- Output to a reusable SQLite database `data.db` (and optionally CSV via the same parsing pipeline).

## Inputs
- JSON source: `c:\Users\user\Downloads\F-A0010-001.json` (modifiable via CLI flag).

## Outputs
- SQLite database: `data.db` (path configurable via CLI flag).
- Tables are created/kept up to date on every run; existing rows for the same region+date are replaced.

## Database Schema
- `locations`
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `name` TEXT NOT NULL UNIQUE
- `daily_temperatures`
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `location_id` INTEGER NOT NULL REFERENCES `locations`(`id`)
  - `date` TEXT NOT NULL (YYYY-MM-DD)
  - `max_temp_c` REAL
  - `min_temp_c` REAL
  - UNIQUE(`location_id`, `date`)
- Index recommendation (created by the app): `idx_daily_temperatures_loc_date` on (`location_id`, `date`).

## Data Flow
1. Load JSON (UTF-8).
2. Read `cwaopendata.resources.resource.data.agrWeatherForecasts.weatherForecasts.location`.
3. For each `location`:
   - Insert/lookup `locations.name`.
   - Zip `MaxT.daily` and `MinT.daily` by date and insert into `daily_temperatures`.
4. Commit the transaction.

## How to Run
```powershell
# basic run with defaults (JSON in Downloads, DB in current directory)
python app.py

# specify custom paths
python app.py --json "c:\\Users\\user\\Downloads\\F-A0010-001.json" --db "c:\\Users\\user\\Downloads\\data.db"
```

## Notes
- Re-running the app is idempotent for the same data: duplicates are replaced by the UNIQUE constraint.
- Extendable: add more weather elements (e.g., rainfall) by expanding the insert loop and schema.

"""Load F-A0010-001 JSON and store region temperatures into SQLite."""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_JSON = Path("F-A0010-001.json")
DEFAULT_DB = Path("data.db")


def to_float(value: Any) -> float:
    """Convert string/number to float, treating empty values as None."""
    if value in ("", None):
        return None  # type: ignore[return-value]
    return float(value)


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS daily_temperatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            max_temp_c REAL,
            min_temp_c REAL,
            UNIQUE(location_id, date),
            FOREIGN KEY(location_id) REFERENCES locations(id)
        );

        CREATE INDEX IF NOT EXISTS idx_daily_temperatures_loc_date
            ON daily_temperatures(location_id, date);
        """
    )
    conn.commit()


def load_locations(json_path: Path) -> List[Dict[str, Any]]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    try:
        return (
            data["cwaopendata"]["resources"]["resource"]["data"]
            ["agrWeatherForecasts"]["weatherForecasts"]["location"]
        )
    except KeyError as exc:
        raise KeyError(f"Unexpected JSON structure: missing {exc}") from exc


def insert_data(conn: sqlite3.Connection, locations: List[Dict[str, Any]]) -> None:
    cur = conn.cursor()
    for loc in locations:
        name = loc["locationName"]
        cur.execute("INSERT OR IGNORE INTO locations(name) VALUES (?)", (name,))
        cur.execute("SELECT id FROM locations WHERE name = ?", (name,))
        location_id = cur.fetchone()[0]

        max_daily = loc["weatherElements"]["MaxT"]["daily"]
        min_daily = loc["weatherElements"]["MinT"]["daily"]

        for max_entry, min_entry in zip(max_daily, min_daily):
            cur.execute(
                """
                INSERT OR REPLACE INTO daily_temperatures
                (location_id, date, max_temp_c, min_temp_c)
                VALUES (?, ?, ?, ?)
                """,
                (
                    location_id,
                    max_entry["dataDate"],
                    to_float(max_entry["temperature"]),
                    to_float(min_entry["temperature"]),
                ),
            )
    conn.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse F-A0010-001 JSON and store temperatures into SQLite."
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help=f"Path to F-A0010-001.json (default: {DEFAULT_JSON})",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Output SQLite path (default: {DEFAULT_DB})",
    )
    return parser.parse_args()


def resolve_json(path: Path) -> Path:
    """Find JSON file in common locations: given path, CWD, script directory."""
    candidates = [
        path,
        Path.cwd() / path,
        Path(__file__).resolve().parent / path.name,
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    raise FileNotFoundError(
        f"JSON file not found. Tried: {', '.join(str(c) for c in candidates)}"
    )


def main() -> None:
    args = parse_args()
    json_path = resolve_json(args.json)
    locations = load_locations(json_path)
    with sqlite3.connect(args.db) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        ensure_schema(conn)
        insert_data(conn, locations)
    print(f"Wrote {len(locations)} locations to {args.db}")


if __name__ == "__main__":
    main()

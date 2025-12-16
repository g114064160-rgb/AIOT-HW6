# Operations Guide

## Install
```bash
pip install -r requirements.txt
```

## Ingest (build/refresh SQLite)
```bash
# default: uses repo-local JSON, outputs data.db in CWD
python app.py

# custom paths
python app.py --json /path/to/F-A0010-001.json --db /path/to/data.db
```

## Streamlit UI (read-only viewer)
```bash
streamlit run streamlit_app.py
```
- Change DB path in the UI if needed (defaults to `data.db`).
- Filter by location or view all.

## Deployment (Streamlit Cloud)
1) Push repo (contains sample JSON).
2) In Streamlit Cloud, set repo to `g114064160-rgb/AIOT-HW6`, branch `main`, app file `streamlit_app.py`.
3) Python version: 3.10+; requirements from `requirements.txt`.
4) If using live JSON, add it to the repo or host it and update DB path after ingest.

## Common Issues
- FileNotFoundError (ingest): provide `--json` with a valid path.
- No data in UI: ensure `data.db` exists and has rows (run `python app.py` first).
- Wrong DB path in UI: update the path field to point to the correct SQLite file.

## Maintenance
- Schema migrations: adjust `ensure_schema` in `app.py`; consider versioning.
- Backups: copy `data.db` periodically; SQLite is a single-file DB.
- Indexes: already includes (`location_id`, `date`); add more if queries expand.

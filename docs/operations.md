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
- 可在 UI 修改 DB 路徑（預設 `data.db`）與 JSON 路徑。
- 若 DB 不存在，會嘗試自動用 JSON 匯入；亦可按「重新匯入」強制覆寫同日期資料。
- Filter by location or view all.

## Deployment (Streamlit Cloud)
1) Push repo (contains sample JSON).
2) In Streamlit Cloud, set repo to `g114064160-rgb/AIOT-HW6`, branch `main`, app file `streamlit_app.py`.
3) Python version: 3.10+; requirements from `requirements.txt`.
4) If using live JSON, add it to the repo or host it and update DB path after ingest.

## Common Issues
- FileNotFoundError (ingest): provide `--json` with a valid path, or place `F-A0010-001.json` beside `app.py`.
- No data in UI: DB 可能不存在或無資料，UI 會提示並可直接匯入。
- Wrong DB path in UI:更新 DB 路徑或 JSON 路徑後重新匯入。

## Maintenance
- Schema migrations: adjust `ensure_schema` in `app.py`; consider versioning.
- Backups: copy `data.db` periodically; SQLite is a single-file DB.
- Indexes: already includes (`location_id`, `date`); add more if queries expand.

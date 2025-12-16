# AIOT-HW6

從 CWA F-A0010-001 JSON 解析各地區每日高低溫，寫入 SQLite，並以 Streamlit 介面瀏覽。

## 環境
```bash
pip install -r requirements.txt
```

## 主要腳本
- `app.py`：讀取 `F-A0010-001.json`，寫入 `data.db`（表 `locations`、`daily_temperatures`）。預設 JSON 路徑為專案內的 `F-A0010-001.json`，可用 `--json` 指定其他檔案；`--db` 可指定輸出 DB。
  ```bash
  python app.py
  # or
  python app.py --json /path/to/F-A0010-001.json --db /path/to/data.db
  ```
- `ui/streamlit_app.py`：從 SQLite 讀取資料並顯示表格，可在 UI 中改 DB 路徑（預設 `data.db`）。
  ```bash
  streamlit run ui/streamlit_app.py
  ```

## 資料表設計
- `locations(id, name UNIQUE)`
- `daily_temperatures(id, location_id, date, max_temp_c, min_temp_c, UNIQUE(location_id, date))`

## 進階文件
- 系統架構：`docs/architecture.md`
- 操作手冊：`docs/operations.md`

"""Streamlit app to view temperatures stored in SQLite (data.db)."""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Tuple

import streamlit as st

import app as ingest  # reuse ingestion utilities


DEFAULT_DB = Path("data.db")
DEFAULT_JSON = Path("F-A0010-001.json")


def resolve_json(path: Path) -> Path | None:
    candidates = [
        path,
        Path.cwd() / path,
        Path(__file__).resolve().parent / path.name,
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    return None


def load_locations(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT name FROM locations ORDER BY name")
    return [row[0] for row in cur.fetchall()]


def load_temperatures(
    conn: sqlite3.Connection, location: str | None
) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    query = """
        SELECT l.name, t.date, t.max_temp_c, t.min_temp_c
        FROM daily_temperatures t
        JOIN locations l ON l.id = t.location_id
    """
    params: Tuple[Any, ...] = ()
    if location:
        query += " WHERE l.name = ?"
        params = (location,)
    query += " ORDER BY t.date, l.id"

    cur.execute(query, params)
    rows = cur.fetchall()
    return [
        {
            "地區": name,
            "日期": date,
            "最高溫(°C)": max_temp,
            "最低溫(°C)": min_temp,
        }
        for name, date, max_temp, min_temp in rows
    ]


def ingest_json_to_db(db_path: Path, json_path: Path) -> str:
    json_actual = ingest.ensure_json(json_path)
    locations = ingest.load_locations(json_actual)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        ingest.ensure_schema(conn)
        ingest.insert_data(conn, locations)
    return f"已匯入 {len(locations)} 個地區到 {db_path} (JSON: {json_actual})"


def main() -> None:
    st.title("CWA 農業氣象 - SQLite 資料瀏覽")
    st.caption("來源：data.db (若不存在，可從 JSON 匯入)")

    col1, col2 = st.columns(2)
    with col1:
        db_path_str = st.text_input("SQLite 路徑", value=str(DEFAULT_DB))
    with col2:
        json_path_str = st.text_input("JSON 路徑（用於匯入）", value=str(DEFAULT_JSON))

    db_path = Path(db_path_str).expanduser()
    json_path_candidate = resolve_json(Path(json_path_str).expanduser())

    if not db_path.exists():
        st.warning(f"找不到資料庫檔案: {db_path}")
        if json_path_candidate:
            try:
                msg = ingest_json_to_db(db_path, json_path_candidate)
                st.success(msg)
            except Exception as exc:  # noqa: BLE001
                st.exception(exc)
                return
        else:
            st.info("請提供有效的 JSON 路徑並按下『重新匯入』按鈕。")
            return

    if st.button("重新匯入（覆寫相同日期資料）"):
        if not json_path_candidate:
            st.error("找不到 JSON 檔案，請確認路徑。")
        else:
            try:
                msg = ingest_json_to_db(db_path, json_path_candidate)
                st.success(msg)
            except Exception as exc:  # noqa: BLE001
                st.exception(exc)

    try:
        conn = sqlite3.connect(db_path)
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
        return

    with conn:
        locations = load_locations(conn)
        if not locations:
            st.warning("資料庫目前沒有地區資料，請先匯入。")
            return

        st.success(f"已載入 {len(locations)} 個地區")

        selected = st.selectbox("選擇地區", ["全部"] + locations)
        filter_loc = None if selected == "全部" else selected

        data = load_temperatures(conn, filter_loc)
        st.write(f"筆數：{len(data)}")
        st.dataframe(data, hide_index=True)


if __name__ == "__main__":
    main()

"""Streamlit app to view temperatures stored in SQLite (data.db)."""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Tuple

import streamlit as st


DEFAULT_DB = Path("data.db")


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


def main() -> None:
    st.title("CWA 農業氣象 - SQLite 資料瀏覽")
    st.caption("來源：data.db (由 app.py 寫入)")

    db_path_str = st.text_input("SQLite 路徑", value=str(DEFAULT_DB))
    db_path = Path(db_path_str).expanduser()

    if not db_path.exists():
        st.error(f"找不到資料庫檔案: {db_path}")
        st.info("請先執行 app.py 產生 data.db 或調整路徑。")
        return

    try:
        conn = sqlite3.connect(db_path)
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
        return

    with conn:
        locations = load_locations(conn)
        st.success(f"已載入 {len(locations)} 個地區")

        selected = st.selectbox("選擇地區", ["全部"] + locations)
        filter_loc = None if selected == "全部" else selected

        data = load_temperatures(conn, filter_loc)
        st.write(f"筆數：{len(data)}")
        st.dataframe(data, hide_index=True)


if __name__ == "__main__":
    main()

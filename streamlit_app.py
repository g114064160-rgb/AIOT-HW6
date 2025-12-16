"""Streamlit app to view F-A0010-001 region temperatures."""

from pathlib import Path
import json
from typing import Any, Dict, List

import streamlit as st


DEFAULT_JSON = Path(r"c:\Users\user\Downloads\F-A0010-001.json")


def load_locations(json_path: Path) -> List[Dict[str, Any]]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    try:
        return (
            data["cwaopendata"]["resources"]["resource"]["data"]
            ["agrWeatherForecasts"]["weatherForecasts"]["location"]
        )
    except KeyError as exc:
        raise KeyError(f"Unexpected JSON structure: missing {exc}") from exc


def main() -> None:
    st.title("CWA 農業氣象 - 各地區溫度")
    st.caption("來源：F-A0010-001 JSON")

    json_path_str = st.text_input("JSON 路徑", value=str(DEFAULT_JSON))
    json_path = Path(json_path_str).expanduser()

    if not json_path.exists():
        st.error(f"檔案不存在: {json_path}")
        return

    try:
        locations = load_locations(json_path)
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
        return

    st.success(f"已載入 {len(locations)} 個地區")

    for loc in locations:
        name = loc["locationName"]
        max_daily = loc["weatherElements"]["MaxT"]["daily"]
        min_daily = loc["weatherElements"]["MinT"]["daily"]

        rows = []
        for max_entry, min_entry in zip(max_daily, min_daily):
            rows.append(
                {
                    "日期": max_entry["dataDate"],
                    "最高溫(°C)": float(max_entry["temperature"]),
                    "最低溫(°C)": float(min_entry["temperature"]),
                }
            )

        st.subheader(name)
        st.dataframe(rows, hide_index=True)


if __name__ == "__main__":
    main()

"""主 Streamlit 應用。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import streamlit as st

from src.io import load_excel, profile_sheets, consolidate_frames
st.set_page_config(page_title="經濟行為研究儀表板", layout="wide")

if "data_frames" not in st.session_state:
    st.session_state["data_frames"] = {}
if "active_df" not in st.session_state:
    st.session_state["active_df"] = None

st.sidebar.title("全域控制")

uploaded = st.sidebar.file_uploader("上傳 Excel", type=["xlsx", "xlsm"], help="支援多工作表自動辨識")
if uploaded:
    temp_path = Path("data/uploaded.xlsx")
    temp_path.write_bytes(uploaded.getbuffer())
    frames = load_excel(temp_path)
    st.session_state["data_frames"] = frames
    st.session_state["active_df"] = consolidate_frames(frames)

if st.session_state["data_frames"]:
    sheet_profiles = profile_sheets(st.session_state["data_frames"])
    st.sidebar.success(f"已載入 {len(sheet_profiles)} 個工作表")
    if st.sidebar.button("匯出資料字典"):
        payload = [profile.to_dict() for profile in sheet_profiles]
        st.sidebar.download_button("下載 JSON", json.dumps(payload, ensure_ascii=False, indent=2), file_name="data_dictionary.json")

st.title("經濟行為研究儀表板")

if st.session_state["active_df"] is None:
    st.info("請上傳資料檔或於 pages/00_Data_Profile.py 建立更多清理流程。")
else:
    df = st.session_state["active_df"]
    st.write("目前資料筆數：", df.shape[0])
    st.write(df.head())

st.markdown("本應用提供各式研究模組，請由左側頁面導覽。")

"""資料剖析與清理頁面。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.io import load_excel, profile_sheets, consolidate_frames, export_profiles
from src.cleaning import (
    normalize_column_names,
    apply_column_mapping,
    fill_missing_numeric,
    fill_missing_categorical,
    remove_duplicates,
    standardize_numeric,
)

st.set_page_config(page_title="資料設定", layout="wide")

if "data_frames" not in st.session_state:
    st.session_state["data_frames"] = {}
if "active_df" not in st.session_state:
    st.session_state["active_df"] = None
if "cleaning_log" not in st.session_state:
    st.session_state["cleaning_log"] = []

st.title("資料 Profiling 與清理")

uploaded = st.file_uploader("重新上傳資料檔", type=["xlsx", "xlsm"], help="支援自動偵測工作表")
if uploaded:
    path = Path("data/uploaded.xlsx")
    path.write_bytes(uploaded.getbuffer())
    st.session_state["data_frames"] = load_excel(path)
    st.session_state["active_df"] = consolidate_frames(st.session_state["data_frames"])

frames = st.session_state.get("data_frames", {})
if not frames:
    st.info("尚未載入資料。請於側邊欄或此頁面上傳檔案。")
    st.stop()

profiles = profile_sheets(frames)
with st.expander("工作表摘要", expanded=True):
    for profile in profiles:
        st.subheader(profile.name)
        st.write(f"列數：{profile.rows}，欄數：{profile.cols}")
        st.dataframe(profile.sample)
        st.json(profile.to_dict())

if st.button("匯出資料字典 JSON"):
    export_path = export_profiles(profiles, "outputs/data_dictionary.json")
    st.download_button("下載", data=Path(export_path).read_text(encoding="utf-8"), file_name="data_dictionary.json")

with st.expander("欄位命名標準化"):
    if st.session_state["active_df"] is not None:
        mapping = normalize_column_names(st.session_state["active_df"].columns)
        st.json(mapping)
        if st.button("套用欄位映射"):
            st.session_state["active_df"] = apply_column_mapping(st.session_state["active_df"], mapping)
            st.success("已套用欄位名稱映射。")

with st.expander("缺失值處理"):
    if st.session_state["active_df"] is not None:
        df = st.session_state["active_df"]
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(exclude="number").columns.tolist()
        method = st.selectbox("數值補值方法", ["median", "mean"])
        if st.button("補齊數值缺失"):
            log = fill_missing_numeric(df, numeric_cols, method)
            st.session_state["cleaning_log"].extend(log.operations)
            st.success("已補齊數值缺失")
        if st.button("補齊類別缺失"):
            log = fill_missing_categorical(df, cat_cols)
            st.session_state["cleaning_log"].extend(log.operations)
            st.success("已補齊類別缺失")

with st.expander("重複值與標準化"):
    if st.session_state["active_df"] is not None:
        df = st.session_state["active_df"]
        if st.button("移除重複值"):
            log = remove_duplicates(df)
            st.session_state["cleaning_log"].extend(log.operations)
            st.success("已處理重複值")
        if st.button("標準化數值欄位"):
            log = standardize_numeric(df, df.select_dtypes(include="number").columns)
            st.session_state["cleaning_log"].extend(log.operations)
            st.success("已標準化數值欄位")

if st.session_state["cleaning_log"]:
    st.subheader("清理紀錄")
    st.write("\n".join(f"- {msg}" for msg in st.session_state["cleaning_log"]))

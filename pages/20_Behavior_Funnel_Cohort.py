"""漏斗與 Cohort 分析頁面。"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.kpis import retention, funnel_counts
from src.viz import funnel_chart, retention_curve

st.set_page_config(page_title="漏斗與留存", layout="wide")

st.title("轉換漏斗與 Cohort 分析")

if "active_df" not in st.session_state or st.session_state["active_df"] is None:
    st.warning("請先在資料頁載入資料。")
    st.stop()

df = st.session_state["active_df"]

st.subheader("轉換漏斗")
stages = st.multiselect("選擇漏斗欄位 (布林或是否完成)", options=df.columns)
if stages:
    funnel_df = funnel_counts(df, stages)
    st.plotly_chart(funnel_chart(funnel_df["stage"], funnel_df["value"], "漏斗"), use_container_width=True)
    st.dataframe(funnel_df)
else:
    st.info("請選擇至少一個欄位作為漏斗。")

st.subheader("Cohort 留存")
user_col = st.selectbox("客戶欄位", options=df.columns)
date_col = st.selectbox("日期欄位", options=df.select_dtypes(include="datetime").columns)
freq = st.selectbox("頻率", ["W", "M", "Q"], index=1)
ret = retention(df, user_id=user_col, date_col=date_col, freq=freq)
ret_long = ret.melt(id_vars="cohort", var_name="period", value_name="retention")
st.plotly_chart(retention_curve(ret_long, "cohort", "period", "retention"), use_container_width=True)
st.dataframe(ret)

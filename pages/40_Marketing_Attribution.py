"""行銷歸因頁面。"""
from __future__ import annotations

import streamlit as st
from src.attribution import rule_based_attribution, regression_attribution
from src.viz import bar_chart

st.set_page_config(page_title="行銷歸因", layout="wide")

st.title("多觸點行銷歸因")

if "active_df" not in st.session_state or st.session_state["active_df"] is None:
    st.warning("請先在資料頁載入資料。")
    st.stop()

df = st.session_state["active_df"]

path_col = st.selectbox("路徑欄位", options=df.columns)
revenue_col = st.selectbox("營收欄位", options=df.select_dtypes(include="number").columns)
rule = st.selectbox("歸因規則", options=["last_touch", "first_touch", "linear", "time_decay"])

if st.button("計算歸因"):
    rb = rule_based_attribution(df, path_col=path_col, revenue_col=revenue_col, rule=rule)
    st.dataframe(rb)
    if not rb.empty:
        st.plotly_chart(bar_chart(rb, "channel", "歸因營收", "Rule-based 歸因"), use_container_width=True)

st.subheader("回歸比對")
channel_cols = st.multiselect("通路指標欄位", options=df.select_dtypes(include="number").columns, help="請選擇各通路曝光或成本欄位")
if channel_cols and st.button("回歸分析"):
    params = regression_attribution(df.dropna(subset=channel_cols + [revenue_col]), y=revenue_col, channels=channel_cols)
    st.json(params.to_dict())

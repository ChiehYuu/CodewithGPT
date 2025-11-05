"""價格彈性與準實驗頁面。"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.elasticity import estimate_price_elasticity
from src.econometrics import diff_in_diff

st.set_page_config(page_title="價格彈性", layout="wide")

st.title("價格彈性與準實驗分析")

if "active_df" not in st.session_state or st.session_state["active_df"] is None:
    st.warning("請先在資料頁載入資料。")
    st.stop()

df = st.session_state["active_df"]

st.subheader("價格彈性估計")
qty_col = st.selectbox("銷量欄位", options=df.select_dtypes(include="number").columns)
price_col = st.selectbox("價格欄位", options=df.select_dtypes(include="number").columns, index=1 if df.select_dtypes(include="number").shape[1] > 1 else 0)
control_cols = st.multiselect("控制變數", options=[col for col in df.columns if col not in (qty_col, price_col)])
if st.button("估計彈性"):
    result = estimate_price_elasticity(df, quantity=qty_col, price=price_col, controls=control_cols)
    st.metric("價格彈性", f"{result.elasticity:.2f}")
    st.text(result.model_summary)

st.subheader("差異中的差異 (DID)")
outcome_col = st.selectbox("成果指標", options=df.select_dtypes(include="number").columns)
treat_col = st.selectbox("處理組欄位", options=df.columns)
time_col = st.selectbox("時間欄位", options=df.select_dtypes(include="datetime").columns)
df["treat"] = df[treat_col].astype(int)
df["post"] = pd.to_datetime(df[time_col]) >= pd.to_datetime(df[time_col]).median()
df["interaction"] = df["treat"] * df["post"].astype(int)
formula = f"{outcome_col} ~ treat + post + interaction"
if st.button("執行 DID"):
    did = diff_in_diff(df, formula, cluster=None)
    st.json(did.to_dict())

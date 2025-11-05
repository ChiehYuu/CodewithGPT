"""描述性分析頁面。"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.kpis import basic_kpis, marketing_response
from src.viz import time_series, bar_chart, box_plot, scatter

st.set_page_config(page_title="描述性分析", layout="wide")

st.title("整體概況與分群切片")

if "active_df" not in st.session_state or st.session_state["active_df"] is None:
    st.warning("請先在資料頁載入資料。")
    st.stop()

df = st.session_state["active_df"]

with st.sidebar:
    user_id = st.selectbox("使用者欄位", options=df.columns, index=0)
    order_id = st.selectbox("交易識別欄位", options=df.columns, index=1 if df.shape[1] > 1 else 0)
    revenue_col = st.selectbox("營收欄位", options=df.columns, index=2 if df.shape[1] > 2 else 0)
    gp_col = st.selectbox("毛利欄位", options=["(無)"] + list(df.columns))
    gp_col = None if gp_col == "(無)" else gp_col

metrics = basic_kpis(df, user_id=user_id, order_id=order_id, revenue=revenue_col, gross_profit=gp_col)

metric_cols = st.columns(len(metrics))
for (name, value), col in zip(metrics.items(), metric_cols):
    col.metric(label=name, value=f"{value:,.2f}")

if st.checkbox("顯示時間序列", value=True):
    date_cols = df.select_dtypes(include="datetime").columns
    if not date_cols.empty:
        date_col = st.selectbox("日期欄位", options=date_cols)
        freq = st.selectbox("頻率", ["D", "W", "M"], index=2)
        grouped = df.groupby(pd.Grouper(key=date_col, freq=freq))[revenue_col].sum().reset_index()
        st.plotly_chart(time_series(grouped, date_col, [revenue_col], "營收時間序列"), use_container_width=True)

st.subheader("分群指標")
segment_col = st.selectbox("分群欄位", options=df.columns)
agg_col = st.selectbox("分析指標", options=[revenue_col] + [col for col in df.columns if df[col].dtype.kind in "biufc"])
agg_df = df.groupby(segment_col)[agg_col].agg(["count", "sum", "mean"]).reset_index()
st.plotly_chart(bar_chart(agg_df, segment_col, "sum", f"{segment_col} × {agg_col}"), use_container_width=True)
st.plotly_chart(box_plot(df[[segment_col, agg_col]].dropna(), segment_col, agg_col, "分佈"), use_container_width=True)

st.subheader("行銷觸達 × 客群")
if "channel" in df.columns and "response" in df.columns:
    mr = marketing_response(df, "channel", "response")
    st.plotly_chart(bar_chart(mr, "channel", "回應率", "通路回應率"), use_container_width=True)
else:
    st.info("請確保資料包含 channel 與 response 欄位以進行觸達分析。")

st.subheader("散佈圖")
x_col = st.selectbox("X 軸", options=df.select_dtypes(include="number").columns, key="scatter_x")
y_col = st.selectbox("Y 軸", options=df.select_dtypes(include="number").columns, key="scatter_y")
color_col = st.selectbox("顏色欄位", options=[None] + list(df.columns), key="scatter_color")
size_col = st.selectbox("大小欄位", options=[None] + list(df.select_dtypes(include="number").columns), key="scatter_size")
st.plotly_chart(scatter(df.dropna(subset=[x_col, y_col]), x_col, y_col, color_col, size_col, "散佈分析"), use_container_width=True)

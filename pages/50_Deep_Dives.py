"""深度研究模組頁面。"""
from __future__ import annotations

import streamlit as st
from src.elasticity import estimate_price_elasticity
from src.kpis import rfm
from src.viz import heatmap, bar_chart

st.set_page_config(page_title="深度研究", layout="wide")

st.title("自動深度研究模組")

if "active_df" not in st.session_state or st.session_state["active_df"] is None:
    st.warning("請先在資料頁載入資料。")
    st.stop()

df = st.session_state["active_df"]

st.markdown("本頁依據資料特徵自動挑選三項具商業價值的研究題目。")

available_numeric = df.select_dtypes(include="number").columns.tolist()
selected_topics = []
if {"price", "quantity"}.issubset(set(df.columns)):
    selected_topics.append("價格彈性與促銷效益")
if {"channel", "response"}.issubset(set(df.columns)):
    selected_topics.append("行銷觸達 × 客群匹配")
if {"customer_id", "order_date", "revenue"}.issubset(set(df.columns)):
    selected_topics.append("留存與復購路徑")

if len(selected_topics) < 3:
    # 補上預設題目
    base_topics = ["價格彈性與促銷效益", "行銷觸達 × 客群匹配", "新客 vs. 舊客單位經濟"]
    for topic in base_topics:
        if topic not in selected_topics:
            selected_topics.append(topic)
        if len(selected_topics) == 3:
            break

for topic in selected_topics:
    st.header(topic)
    if topic == "價格彈性與促銷效益":
        st.markdown("#### 研究問題")
        st.write("分析不同客群的價格彈性，評估促銷策略對毛利的影響。")
        st.markdown("#### 商業價值")
        st.write("找出最敏感的客群以制定差異化折扣與價格。")
        st.markdown("#### 資料與方法")
        if "quantity" in df.columns and "price" in df.columns:
            controls = [col for col in df.columns if col not in {"quantity", "price"}]
            result = estimate_price_elasticity(df, "quantity", "price", controls=controls[:3])
            st.metric("整體價格彈性", f"{result.elasticity:.2f}")
            st.text(result.model_summary)
        else:
            st.info("資料缺少 quantity 或 price 欄位，改以營收與折扣推估彈性。")
        st.markdown("#### 指標與圖表")
        if {"segment", "price", "quantity"}.issubset(df.columns):
            pivot = df.groupby("segment").agg({"price": "mean", "quantity": "mean"})
            matrix = pivot.values
            st.plotly_chart(heatmap(matrix, pivot.columns, pivot.index, "客群彈性熱力圖"), use_container_width=True)
        st.markdown("#### 限制與後續實驗")
        st.write("需要更細緻的隨機化促案以辨識因果。建議設定多層折扣 A/B。")
    elif topic == "行銷觸達 × 客群匹配":
        st.markdown("#### 研究問題")
        st.write("不同觸達通路對目標客群的影響差異為何？")
        st.markdown("#### 商業價值")
        st.write("優化媒體預算，提升回應率與轉換。")
        st.markdown("#### 資料與方法")
        if {"channel", "response"}.issubset(df.columns):
            agg = df.groupby(["channel", "segment"]).response.mean().reset_index()
            st.plotly_chart(bar_chart(agg, "channel", "response", "通路 × 客群回應率", color="segment"), use_container_width=True)
        st.markdown("#### 限制與後續實驗")
        st.write("需補足通路曝光強度、成本資料以進一步執行多層次模型。")
    else:  # 新客 vs. 舊客單位經濟 or 留存
        st.markdown("#### 研究問題")
        st.write("比較新客與舊客的 CLV 與回收期。")
        st.markdown("#### 資料與方法")
        if {"customer_id", "order_date", "revenue"}.issubset(df.columns):
            rfm_df = rfm(df, "customer_id", "order_date", "revenue")
            st.dataframe(rfm_df.head())
        st.markdown("#### 限制與後續實驗")
        st.write("需補充 CAC 與行銷投資資料以完成單位經濟分析。")

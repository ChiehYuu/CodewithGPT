"""策略建議頁面。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.recs import generate_recommendations

st.set_page_config(page_title="策略建議", layout="wide")

st.title("策略建議面板")

default_insights = [
    "高價位客群彈性較低，可考慮 premium 定價",
    "某通路回應率低於平均，需重新配置預算",
    "舊客 CLV 高於新客，建議強化留存計畫",
]
report_path = Path("outputs/insights_report.md")
if report_path.exists():
    default_insights.extend(line.strip("- ") for line in report_path.read_text(encoding="utf-8").splitlines() if line.startswith("- "))

insight_log = st.session_state.get("insights", default_insights)

recommendations = generate_recommendations(insight_log)
for rec in recommendations:
    st.write(f"- {rec}")

if st.button("匯出 Markdown 報告"):
    report = "# 洞察報告\n\n" + "\n".join(f"- {insight}" for insight in insight_log)
    st.download_button("下載報告", data=report, file_name="insights.md")

"""視覺化工具。"""
from __future__ import annotations

from typing import Iterable, Optional

try:  # pragma: no cover
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 與 plotly 套件才能繪圖。") from exc


COLOR_SEQ = px.colors.qualitative.Safe


def time_series(df: pd.DataFrame, x: str, y: Iterable[str], title: str) -> go.Figure:
    fig = go.Figure()
    for idx, col in enumerate(y):
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=col, mode="lines+markers", line=dict(color=COLOR_SEQ[idx % len(COLOR_SEQ)])))
    fig.update_layout(title=title, xaxis_title=x, yaxis_title="值", hovermode="x unified")
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: Optional[str] = None, barmode: str = "group") -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, barmode=barmode, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(title=title)
    return fig


def box_plot(df: pd.DataFrame, x: str, y: str, title: str, color: Optional[str] = None) -> go.Figure:
    fig = px.box(df, x=x, y=y, color=color, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(title=title)
    return fig


def heatmap(matrix, x_labels: Iterable[str], y_labels: Iterable[str], title: str) -> go.Figure:
    fig = go.Figure(data=go.Heatmap(z=matrix, x=list(x_labels), y=list(y_labels), colorscale="RdBu"))
    fig.update_layout(title=title)
    return fig


def funnel_chart(stages: Iterable[str], values: Iterable[float], title: str) -> go.Figure:
    fig = go.Figure(go.Funnel(y=list(stages), x=list(values)))
    fig.update_layout(title=title)
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color: Optional[str], size: Optional[str], title: str) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, color=color, size=size, color_discrete_sequence=COLOR_SEQ, trendline="ols")
    fig.update_layout(title=title)
    return fig


def retention_curve(df: pd.DataFrame, cohort_col: str, period_col: str, value_col: str) -> go.Figure:
    pivot = df.pivot_table(index=cohort_col, columns=period_col, values=value_col, aggfunc="mean")
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Blues")
    fig.update_layout(title="留存熱力圖", xaxis_title="週期", yaxis_title="Cohort")
    return fig


def download_figure(fig: go.Figure, path: str) -> str:
    fig.write_image(path)
    return path


__all__ = [
    "time_series",
    "bar_chart",
    "box_plot",
    "heatmap",
    "funnel_chart",
    "scatter",
    "retention_curve",
    "download_figure",
]

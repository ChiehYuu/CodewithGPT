"""核心 KPI 計算。"""
from __future__ import annotations

from typing import Dict, Iterable, Optional

try:  # pragma: no cover
    import pandas as pd
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 套件。") from exc


def basic_kpis(df: pd.DataFrame, *, user_id: str, order_id: str, revenue: str, gross_profit: Optional[str] = None) -> Dict[str, float]:
    total_users = df[user_id].nunique(dropna=True)
    total_orders = df[order_id].nunique(dropna=True)
    total_revenue = float(df[revenue].sum())
    avg_order_value = total_revenue / total_orders if total_orders else 0.0
    metrics = {
        "客戶數": float(total_users),
        "交易數": float(total_orders),
        "營收": total_revenue,
        "客單價": avg_order_value,
    }
    if gross_profit and gross_profit in df:
        total_gp = float(df[gross_profit].sum())
        metrics["毛利"] = total_gp
        metrics["毛利率"] = total_gp / total_revenue if total_revenue else 0.0
    return metrics


def retention(df: pd.DataFrame, user_id: str, date_col: str, freq: str = "M") -> pd.DataFrame:
    ts = df[[user_id, date_col]].dropna()
    ts[date_col] = pd.to_datetime(ts[date_col])
    ts[f"period"] = ts[date_col].dt.to_period(freq)
    first = ts.groupby(user_id)["period"].min()
    cohort = ts.merge(first.rename("cohort"), left_on=user_id, right_index=True)
    cohort["cohort_index"] = (cohort["period"] - cohort["cohort"]).apply(lambda p: p.n)
    pivot = cohort.pivot_table(index="cohort", columns="cohort_index", values=user_id, aggfunc="nunique")
    cohort_sizes = pivot.iloc[:, 0]
    retention_matrix = pivot.divide(cohort_sizes, axis=0)
    retention_matrix.index = retention_matrix.index.astype(str)
    retention_matrix.columns = retention_matrix.columns.astype(int)
    return retention_matrix.reset_index().rename_axis(None, axis=1)


def funnel_counts(df: pd.DataFrame, stages: Iterable[str]) -> pd.DataFrame:
    counts = {}
    for col in stages:
        counts[col] = int(df[col].sum()) if pd.api.types.is_bool_dtype(df[col]) else int(df[col].notna().sum())
    return pd.DataFrame({"stage": list(counts.keys()), "value": list(counts.values())})


def marketing_response(df: pd.DataFrame, channel_col: str, response_col: str) -> pd.DataFrame:
    pivot = df.pivot_table(index=channel_col, values=response_col, aggfunc=["mean", "count"])
    pivot.columns = ["回應率", "樣本數"]
    return pivot.reset_index()


def rfm(df: pd.DataFrame, user_id: str, date_col: str, monetary: str) -> pd.DataFrame:
    data = df[[user_id, date_col, monetary]].dropna()
    data[date_col] = pd.to_datetime(data[date_col])
    snapshot_date = data[date_col].max() + pd.Timedelta(days=1)
    grouped = data.groupby(user_id).agg({date_col: "max", monetary: ["sum", "count"]})
    grouped.columns = ["recency_date", "monetary", "frequency"]
    grouped["recency"] = (snapshot_date - grouped["recency_date"]).dt.days
    grouped.drop(columns="recency_date", inplace=True)
    return grouped.reset_index().rename(columns={user_id: "customer_id"})


__all__ = [
    "basic_kpis",
    "retention",
    "funnel_counts",
    "marketing_response",
    "rfm",
]

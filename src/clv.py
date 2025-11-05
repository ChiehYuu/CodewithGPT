"""CLV 與生命週期分析。"""
from __future__ import annotations

from dataclasses import dataclass
try:  # pragma: no cover
    import pandas as pd
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 套件。") from exc


@dataclass
class CLVResult:
    clv: float
    retention_curve: pd.DataFrame


DISCOUNT_RATE = 0.08


def estimate_simple_clv(retention: pd.DataFrame, gross_margin: float, discount_rate: float = DISCOUNT_RATE) -> CLVResult:
    retention = retention.copy()
    retention.sort_values("cohort_index" if "cohort_index" in retention else retention.columns[1], inplace=True)
    curve_col = [col for col in retention.columns if isinstance(col, int)]
    if curve_col:
        retention_curve = retention[["cohort"] + curve_col]
    else:
        retention_curve = retention
    discounted = []
    for period, rate in enumerate(retention_curve.iloc[0, 1:], start=1):
        discounted.append(rate * gross_margin / ((1 + discount_rate) ** period))
    clv_value = float(sum(discounted))
    return CLVResult(clv=clv_value, retention_curve=retention_curve)


def rfm_segmentation(rfm_df: pd.DataFrame) -> pd.DataFrame:
    result = rfm_df.copy()
    result["R_分群"] = pd.qcut(result["recency"], 4, labels=[4, 3, 2, 1])
    result["F_分群"] = pd.qcut(result["frequency"], 4, labels=[1, 2, 3, 4])
    result["M_分群"] = pd.qcut(result["monetary"], 4, labels=[1, 2, 3, 4])
    result["RFM_Score"] = result[["R_分群", "F_分群", "M_分群"]].sum(axis=1)
    return result


__all__ = ["CLVResult", "estimate_simple_clv", "rfm_segmentation"]

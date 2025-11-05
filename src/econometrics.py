"""計量經濟工具。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover
    import pandas as pd
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 與 statsmodels 套件。") from exc


@dataclass
class DIDResult:
    params: pd.Series
    summary: str

    def to_dict(self) -> dict:
        return {"params": self.params.to_dict(), "summary": self.summary}


def diff_in_diff(df: pd.DataFrame, formula: str, *, cluster: Optional[str] = None) -> DIDResult:
    model = smf.ols(formula, data=df).fit(cov_type="HC1")
    if cluster and cluster in df:
        model = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
    return DIDResult(params=model.params, summary=model.summary().as_text())


def fixed_effect(df: pd.DataFrame, formula: str, entity: str, time: str) -> DIDResult:
    dummy_entity = pd.get_dummies(df[entity], prefix=entity, drop_first=True)
    dummy_time = pd.get_dummies(df[time], prefix=time, drop_first=True)
    X = pd.concat([dummy_entity, dummy_time], axis=1)
    y, X = sm.add_constant(df[formula.split('~')[0].strip()]), X
    model = sm.OLS(y, X).fit()
    return DIDResult(params=model.params, summary=model.summary().as_text())


__all__ = ["DIDResult", "diff_in_diff", "fixed_effect"]

"""行銷歸因工具。"""
from __future__ import annotations

from typing import Dict, List

try:  # pragma: no cover
    import pandas as pd
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 套件。") from exc


RULES = {
    "first_touch": lambda touches: touches[0] if touches else None,
    "last_touch": lambda touches: touches[-1] if touches else None,
    "linear": lambda touches: {channel: 1 / len(touches) for channel in touches} if touches else {},
}


def time_decay(touches: List[str], decay: float = 0.5) -> Dict[str, float]:
    weights: Dict[str, float] = {}
    total = 0.0
    for idx, channel in enumerate(reversed(touches)):
        weight = decay ** idx
        weights[channel] = weights.get(channel, 0.0) + weight
        total += weight
    return {channel: weight / total for channel, weight in weights.items()}


def rule_based_attribution(paths: pd.DataFrame, path_col: str, revenue_col: str, rule: str = "last_touch") -> pd.DataFrame:
    records = []
    for _, row in paths.iterrows():
        touches = [touch.strip() for touch in str(row[path_col]).split(" > ") if touch]
        revenue = row.get(revenue_col, 0.0)
        if rule in ("first_touch", "last_touch"):
            channel = RULES[rule](touches)
            if channel:
                records.append({"channel": channel, "weight": 1.0, "revenue": revenue})
        elif rule == "linear":
            weights = RULES[rule](touches)
            for channel, weight in weights.items():
                records.append({"channel": channel, "weight": weight, "revenue": revenue})
        elif rule == "time_decay":
            weights = time_decay(touches)
            for channel, weight in weights.items():
                records.append({"channel": channel, "weight": weight, "revenue": revenue})
        else:
            raise ValueError("不支援的歸因規則")
    df = pd.DataFrame(records)
    if df.empty:
        return df
    return df.groupby("channel").apply(lambda x: (x["weight"] * x["revenue"]).sum()).reset_index(name="歸因營收")


def regression_attribution(df: pd.DataFrame, y: str, channels: List[str]) -> pd.Series:
    X = df[channels]
    X = sm.add_constant(X)
    y_vec = df[y]
    model = sm.OLS(y_vec, X).fit()
    return model.params


try:  # pragma: no cover
    import statsmodels.api as sm
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 statsmodels 套件。") from exc


__all__ = ["rule_based_attribution", "regression_attribution", "time_decay"]

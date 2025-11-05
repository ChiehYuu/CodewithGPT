"""價格彈性分析工具。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover
    import statsmodels.formula.api as smf
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 與 statsmodels 套件。") from exc


@dataclass
class ElasticityResult:
    elasticity: float
    model_summary: str


def estimate_price_elasticity(df: pd.DataFrame, quantity: str, price: str, controls: Optional[list[str]] = None) -> ElasticityResult:
    data = df[[quantity, price] + (controls or [])].dropna()
    data = data[data[price] > 0]
    data = data[data[quantity] > 0]
    data["ln_q"] = np.log(data[quantity])  # type: ignore[name-defined]
    data["ln_p"] = np.log(data[price])
    formula = "ln_q ~ ln_p"
    if controls:
        formula += " + " + " + ".join(controls)
    model = smf.ols(formula, data=data).fit()
    elasticity = float(model.params.get("ln_p", 0.0))
    return ElasticityResult(elasticity=elasticity, model_summary=model.summary().as_text())


try:  # pragma: no cover
    import numpy as np
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 numpy 套件。") from exc


__all__ = ["ElasticityResult", "estimate_price_elasticity"]

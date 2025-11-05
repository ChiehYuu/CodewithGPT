"""策略建議產生器。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


def generate_recommendations(insights: List[str]) -> List[str]:
    recommendations = []
    for insight in insights:
        recommendations.append(f"根據洞察：{insight}，建議執行 A/B 測試以量化 ROI。")
    return recommendations


@dataclass
class StrategyItem:
    title: str
    description: str
    roi: str
    risk: str
    next_step: str


__all__ = ["generate_recommendations", "StrategyItem"]

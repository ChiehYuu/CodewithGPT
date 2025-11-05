"""資料清理工具。"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, Optional

try:  # pragma: no cover
    import pandas as pd
    import numpy as np
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError("需要 pandas 與 numpy 套件才能執行清理功能。") from exc


@dataclass
class CleaningLog:
    """記錄清理過程資訊。"""

    operations: list[str]

    def add(self, message: str) -> None:
        self.operations.append(message)

    def to_markdown(self) -> str:
        items = "\n".join(f"- {msg}" for msg in self.operations)
        return f"### 清理紀錄\n{items}"


def normalize_column_names(columns: Iterable[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for col in columns:
        slug = re.sub(r"[\s\-/]+", "_", col.strip())
        slug = re.sub(r"[^0-9a-zA-Z_]+", "", slug)
        slug = slug.lower()
        mapping[col] = slug
    return mapping


def apply_column_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=mapping)


def fill_missing_numeric(df: pd.DataFrame, columns: Iterable[str], method: str = "median") -> CleaningLog:
    log = CleaningLog([])
    for col in columns:
        if col not in df:
            continue
        if method == "median":
            value = float(df[col].median())
            df[col].fillna(value, inplace=True)
            log.add(f"欄位 {col} 以中位數 {value:.2f} 補值")
        elif method == "mean":
            value = float(df[col].mean())
            df[col].fillna(value, inplace=True)
            log.add(f"欄位 {col} 以平均數 {value:.2f} 補值")
        else:
            raise ValueError("不支援的補值方法")
    return log


def fill_missing_categorical(df: pd.DataFrame, columns: Iterable[str], placeholder: str = "未知") -> CleaningLog:
    log = CleaningLog([])
    for col in columns:
        if col not in df:
            continue
        df[col] = df[col].astype("object").fillna(placeholder)
        log.add(f"欄位 {col} 補上類別 '{placeholder}'")
    return log


def remove_duplicates(df: pd.DataFrame, subset: Optional[Iterable[str]] = None) -> CleaningLog:
    before = df.shape[0]
    df.drop_duplicates(subset=subset, inplace=True)
    after = df.shape[0]
    removed = before - after
    log = CleaningLog([f"移除 {removed} 筆重複資料"])
    return log


def detect_outliers_iqr(series: pd.Series, *, k: float = 1.5) -> pd.Series:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return (series < lower) | (series > upper)


def standardize_numeric(df: pd.DataFrame, columns: Iterable[str]) -> CleaningLog:
    log = CleaningLog([])
    for col in columns:
        if col not in df:
            continue
        mean = df[col].mean()
        std = df[col].std(ddof=0)
        if std == 0:
            continue
        df[col] = (df[col] - mean) / std
        log.add(f"欄位 {col} 標準化 (Z-score)")
    return log


__all__ = [
    "CleaningLog",
    "normalize_column_names",
    "apply_column_mapping",
    "fill_missing_numeric",
    "fill_missing_categorical",
    "remove_duplicates",
    "detect_outliers_iqr",
    "standardize_numeric",
]

"""資料載入與整併工具。"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:  # pragma: no cover - 測試環境若無 pandas 仍給予友善訊息
    import pandas as pd
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "需要 pandas 套件才能執行資料載入。請安裝 pandas>=1.5。"
    ) from exc

LOGGER = logging.getLogger(__name__)


@dataclass
class SheetProfile:
    """紀錄工作表結構摘要。"""

    name: str
    rows: int
    cols: int
    columns: List[str]
    inferred_types: Dict[str, str]
    missing_rates: Dict[str, float]
    sample: pd.DataFrame = field(repr=False)

    def to_dict(self) -> Dict[str, object]:
        """輸出成 dict，方便寫入 JSON 或顯示。"""

        return {
            "sheet": self.name,
            "rows": self.rows,
            "cols": self.cols,
            "columns": self.columns,
            "inferred_types": self.inferred_types,
            "missing_rates": self.missing_rates,
        }


def _infer_type(series: pd.Series) -> str:
    """推斷欄位型別。"""

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    return "categorical"


def load_excel(file_path: Path | str, *, sheet: str | None = None) -> Dict[str, pd.DataFrame]:
    """載入 Excel，支援多工作表。"""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到資料檔案：{path}")

    xls = pd.ExcelFile(path)
    sheets = [sheet] if sheet else xls.sheet_names
    result: Dict[str, pd.DataFrame] = {}
    for name in sheets:
        df = xls.parse(name)
        result[name] = df
    return result


def profile_sheets(frames: Dict[str, pd.DataFrame], *, sample_rows: int = 5) -> List[SheetProfile]:
    """產生工作表結構摘要。"""

    profiles: List[SheetProfile] = []
    for name, df in frames.items():
        inferred = {col: _infer_type(df[col]) for col in df.columns}
        missing = {col: float(df[col].isna().mean()) for col in df.columns}
        sample = df.head(sample_rows)
        profiles.append(
            SheetProfile(
                name=name,
                rows=int(df.shape[0]),
                cols=int(df.shape[1]),
                columns=list(df.columns),
                inferred_types=inferred,
                missing_rates=missing,
                sample=sample,
            )
        )
    return profiles


def consolidate_frames(frames: Dict[str, pd.DataFrame], *, how: str = "outer") -> pd.DataFrame:
    """整併多張工作表。"""

    dfs = list(frames.values())
    if not dfs:
        return pd.DataFrame()
    if len(dfs) == 1:
        return dfs[0]

    base = dfs[0]
    for other in dfs[1:]:
        base = pd.merge(base, other, how=how, left_index=True, right_index=True, suffixes=("", "_dup"))
    return base


def export_profiles(profiles: Iterable[SheetProfile], path: Path | str) -> Path:
    """匯出結構摘要 JSON。"""

    output_path = Path(path)
    payload = [profile.to_dict() for profile in profiles]
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def detect_primary_key(df: pd.DataFrame, *, max_combination: int = 3) -> Optional[Tuple[str, ...]]:
    """尋找可能的主鍵欄位組合。"""

    columns = list(df.columns)
    n = len(columns)
    for r in range(1, min(max_combination, n) + 1):
        for combo in combinations(columns, r):  # type: ignore[name-defined]
            if df[list(combo)].drop_duplicates().shape[0] == df.shape[0]:
                return combo
    return None


# 延遲匯入 combinations 以避免覆寫 typing
from itertools import combinations  # noqa: E402  # isort:skip

__all__ = [
    "SheetProfile",
    "load_excel",
    "profile_sheets",
    "consolidate_frames",
    "export_profiles",
    "detect_primary_key",
]

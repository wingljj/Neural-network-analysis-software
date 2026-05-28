"""数据导入与预处理相关模型。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ExcelLoadConfig:
    """Excel 读取配置。"""

    path: str
    sheet_name: str | int = 0
    header: int | None = 0
    feature_count: int = 0
    target_count: int = 0


@dataclass(frozen=True)
class PreprocessConfig:
    """数据预处理配置。"""

    missing_strategy: str = "mean"
    scaler: str = "standard"
    fill_value: float | None = None

    def __post_init__(self) -> None:
        allowed_missing = {"drop_rows", "mean", "median", "constant"}
        allowed_scalers = {"none", "standard", "minmax"}
        if self.missing_strategy not in allowed_missing:
            raise ValueError(f"missing_strategy 必须为 {sorted(allowed_missing)} 之一")
        if self.scaler not in allowed_scalers:
            raise ValueError(f"scaler 必须为 {sorted(allowed_scalers)} 之一")


@dataclass
class DatasetBundle:
    """原始数据切分结果。"""

    raw: pd.DataFrame
    X: pd.DataFrame
    y: pd.DataFrame
    feature_names: list[str]
    target_names: list[str]


@dataclass
class ProcessedBundle:
    """预处理后的数据和可复用转换器。"""

    raw: pd.DataFrame
    X: pd.DataFrame
    y: pd.DataFrame
    feature_names: list[str]
    target_names: list[str]
    scaler: Any | None = None
    warnings: list[str] | None = None

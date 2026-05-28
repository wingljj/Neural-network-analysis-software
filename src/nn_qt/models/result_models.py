"""分析、训练和预测结果模型。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .train_models import TrainConfig


@dataclass
class PcaResult:
    components: pd.DataFrame
    explained_variance_ratio: list[float]


@dataclass
class AnovaResult:
    f_values: pd.DataFrame
    p_values: pd.DataFrame


@dataclass
class SensitivityResult:
    importance: pd.DataFrame


@dataclass
class ModelPackage:
    model: Any
    scaler: Any | None
    feature_columns: list[str]
    target_columns: list[str]
    train_config: TrainConfig
    metrics: dict[str, float]
    loss_curve: list[float]
    created_at: str
    app_version: str


@dataclass
class TrainResult:
    model_package: ModelPackage
    train_mse: float
    train_r2: float
    test_mse: float
    test_r2: float
    loss_curve: list[float]
    y_test: pd.DataFrame
    y_pred: pd.DataFrame


@dataclass
class PredictionResult:
    predictions: pd.DataFrame
    output_path: str
    inverse_transformed_features: pd.DataFrame | None = None

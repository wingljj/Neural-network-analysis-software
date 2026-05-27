"""通用配置对象。

所有配置都集中定义在这里，UI 层只负责收集用户输入，核心层只接收
这些 dataclass 对象。这样后续扩展新的算法或打包成服务都比较容易。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple


MissingStrategy = Literal["mean", "drop"]
ScalerType = Literal["standard", "minmax", "none"]
TaskType = Literal["regression", "classification"]


@dataclass(frozen=True)
class DataConfig:
    """Excel 数据抽取和预处理配置。"""

    feature_count: int
    target_count: int
    missing_strategy: MissingStrategy = "mean"
    scaler_type: ScalerType = "standard"


@dataclass(frozen=True)
class TrainingConfig:
    """多层感知机训练配置。"""

    task_type: TaskType = "regression"
    hidden_layers: Tuple[int, ...] = (64, 32)
    learning_rate: float = 0.001
    epochs: int = 300
    test_size: float = 0.2
    random_state: int = 42


@dataclass(frozen=True)
class ModelBundle:
    """训练后保存到磁盘的对象。

    scaler 与 model 一起保存，预测新 Excel 时可以复用训练时的同一套
    特征缩放规则，避免训练/预测分布不一致。
    """

    model: object
    scaler: object | None
    feature_names: list[str]
    target_names: list[str]
    task_type: TaskType


@dataclass(frozen=True)
class PredictionResult:
    """预测导出的返回信息。"""

    dataframe_path: Path
    rows: int
    target_names: list[str]

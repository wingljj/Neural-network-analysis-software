"""神经网络训练、评估、保存与加载。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier, MLPRegressor

from nn_analysis_app.core.config import ModelBundle, TrainingConfig
from nn_analysis_app.core.data_io import PreparedDataset


ProgressCallback = Callable[[str], None]


@dataclass
class TrainingResult:
    """训练结果，供 UI 层展示图表和指标。"""

    bundle: ModelBundle
    metrics: dict[str, float]
    y_test: np.ndarray
    y_pred: np.ndarray
    loss_curve: list[float]


def parse_hidden_layers(text: str) -> tuple[int, ...]:
    """把用户输入的隐藏层配置解析成 tuple。

    支持格式示例：64,32 或 128。
    """
    try:
        values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    except ValueError as exc:
        raise ValueError("隐藏层节点数格式错误，请输入如 64,32") from exc

    if not values or any(value <= 0 for value in values):
        raise ValueError("隐藏层节点数必须为正整数")
    return values


def train_mlp(
    dataset: PreparedDataset,
    config: TrainingConfig,
    progress_callback: ProgressCallback | None = None,
) -> TrainingResult:
    """训练基础多层感知机模型。

    scikit-learn 的 MLP 使用 max_iter 表示最大训练轮数，并暴露 loss_curve_，
    已经能满足离线桌面软件的基础神经网络预测需求。
    """
    if progress_callback:
        progress_callback("正在划分训练集和测试集...")

    x_train, x_test, y_train, y_test = train_test_split(
        dataset.scaled_features,
        dataset.targets.to_numpy(),
        test_size=config.test_size,
        random_state=config.random_state,
    )

    y_train_model = _shape_target_for_sklearn(y_train)
    y_test_eval = _shape_target_for_sklearn(y_test)

    if config.task_type == "classification":
        model = MLPClassifier(
            hidden_layer_sizes=config.hidden_layers,
            learning_rate_init=config.learning_rate,
            max_iter=config.epochs,
            random_state=config.random_state,
            early_stopping=True,
        )
    else:
        model = MLPRegressor(
            hidden_layer_sizes=config.hidden_layers,
            learning_rate_init=config.learning_rate,
            max_iter=config.epochs,
            random_state=config.random_state,
            early_stopping=True,
        )

    if progress_callback:
        progress_callback(
            f"开始训练 MLP，隐藏层={config.hidden_layers}，学习率={config.learning_rate}，Epochs={config.epochs}"
        )
    model.fit(x_train, y_train_model)
    y_pred = model.predict(x_test)

    metrics = _evaluate(config.task_type, y_test_eval, y_pred)
    if progress_callback:
        joined = "，".join(f"{key}={value:.4f}" for key, value in metrics.items())
        progress_callback(f"训练完成：{joined}")

    bundle = ModelBundle(
        model=model,
        scaler=dataset.scaler,
        feature_names=dataset.feature_names,
        target_names=dataset.target_names,
        task_type=config.task_type,
    )
    return TrainingResult(
        bundle=bundle,
        metrics=metrics,
        y_test=np.asarray(y_test_eval),
        y_pred=np.asarray(y_pred),
        loss_curve=list(getattr(model, "loss_curve_", [])),
    )


def save_model(bundle: ModelBundle, path: str | Path) -> Path:
    """保存模型、缩放器和列名等元数据。"""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, output_path)
    return output_path


def load_model(path: str | Path) -> ModelBundle:
    """从磁盘加载模型包。"""
    model_path = Path(path)
    if not model_path.exists():
        raise FileNotFoundError(f"模型文件不存在：{model_path}")
    bundle = joblib.load(model_path)
    if not isinstance(bundle, ModelBundle):
        raise TypeError("模型文件格式不正确，请选择本软件保存的 .joblib 文件")
    return bundle


def predict(bundle: ModelBundle, scaled_features: np.ndarray) -> np.ndarray:
    """使用已加载模型执行预测。"""
    return np.asarray(bundle.model.predict(scaled_features))


def metrics_to_dataframe(metrics: dict[str, float]) -> pd.DataFrame:
    """把指标字典转为表格，方便 UI 展示或导出。"""
    return pd.DataFrame(
        [{"metric": key, "value": value} for key, value in metrics.items()]
    )


def _shape_target_for_sklearn(target: np.ndarray) -> np.ndarray:
    """单输出任务转成一维数组，避免 sklearn 发出列向量警告。"""
    arr = np.asarray(target)
    if arr.ndim == 2 and arr.shape[1] == 1:
        return arr.ravel()
    return arr


def _evaluate(task_type: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """计算回归或分类指标。"""
    if task_type == "classification":
        return {"accuracy": float(accuracy_score(y_true, y_pred))}

    return {
        "mse": float(mean_squared_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }

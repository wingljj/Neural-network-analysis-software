"""Excel 读写与数据集拆分。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from nn_analysis_app.core.config import DataConfig


@dataclass
class PreparedDataset:
    """预处理后的训练数据。"""

    raw_dataframe: pd.DataFrame
    features: pd.DataFrame
    targets: pd.DataFrame
    scaled_features: np.ndarray
    scaler: StandardScaler | MinMaxScaler | None
    feature_names: list[str]
    target_names: list[str]


def read_excel(path: str | Path) -> pd.DataFrame:
    """读取 Excel 文件，并尽量保留原始列名。

    pandas 会根据扩展名自动选择 openpyxl/xlrd 等引擎；环境文件中已列出
    这些依赖，方便用户同时读取 .xlsx 和 .xls。
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")
    if file_path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError("仅支持 .xlsx 或 .xls 格式的 Excel 文件")
    return pd.read_excel(file_path)


def prepare_dataset(dataframe: pd.DataFrame, config: DataConfig) -> PreparedDataset:
    """按“前 N 列为输入、后 M 列为输出”的规则生成数据集。"""
    if config.feature_count <= 0:
        raise ValueError("输入变量列数 N 必须大于 0")
    if config.target_count <= 0:
        raise ValueError("输出变量列数 M 必须大于 0")
    if dataframe.empty:
        raise ValueError("Excel 数据为空")

    numeric_df = dataframe.copy()
    numeric_df = numeric_df.apply(pd.to_numeric, errors="coerce")

    expected_cols = config.feature_count + config.target_count
    if numeric_df.shape[1] < expected_cols:
        raise ValueError(
            f"列数不足：当前 {numeric_df.shape[1]} 列，至少需要 {expected_cols} 列"
        )

    # 取前 N 列作为特征，取最后 M 列作为目标，允许中间存在暂不参与的说明列。
    features = numeric_df.iloc[:, : config.feature_count].copy()
    targets = numeric_df.iloc[:, -config.target_count :].copy()

    if config.missing_strategy == "drop":
        combined = pd.concat([features, targets], axis=1).dropna(axis=0)
        features = combined.iloc[:, : config.feature_count]
        targets = combined.iloc[:, -config.target_count :]
    elif config.missing_strategy == "mean":
        features = features.fillna(features.mean(numeric_only=True))
        targets = targets.fillna(targets.mean(numeric_only=True))
    else:
        raise ValueError(f"未知缺失值处理策略：{config.missing_strategy}")

    if features.empty or targets.empty:
        raise ValueError("缺失值处理后没有可用样本")

    scaler: StandardScaler | MinMaxScaler | None
    if config.scaler_type == "standard":
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
    elif config.scaler_type == "minmax":
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)
    elif config.scaler_type == "none":
        scaler = None
        scaled_features = features.to_numpy(dtype=float)
    else:
        raise ValueError(f"未知缩放方式：{config.scaler_type}")

    return PreparedDataset(
        raw_dataframe=dataframe,
        features=features,
        targets=targets,
        scaled_features=scaled_features,
        scaler=scaler,
        feature_names=[str(name) for name in features.columns],
        target_names=[str(name) for name in targets.columns],
    )


def prepare_prediction_features(
    dataframe: pd.DataFrame,
    feature_names: list[str],
    scaler: StandardScaler | MinMaxScaler | None,
) -> np.ndarray:
    """根据已训练模型的特征列准备预测输入。"""
    if len(dataframe.columns) < len(feature_names):
        raise ValueError(
            f"预测文件列数不足：需要至少 {len(feature_names)} 列输入变量"
        )

    features = dataframe.iloc[:, : len(feature_names)].copy()
    features = features.apply(pd.to_numeric, errors="coerce")
    features = features.fillna(features.mean(numeric_only=True))

    if features.isna().any().any():
        raise ValueError("预测数据中存在无法填充的缺失值，请检查输入列")

    if scaler is None:
        return features.to_numpy(dtype=float)
    return scaler.transform(features)


def export_predictions(
    source_dataframe: pd.DataFrame,
    predictions: np.ndarray,
    target_names: list[str],
    output_path: str | Path,
) -> Path:
    """把预测结果追加到原始输入表格后并导出为 Excel。"""
    output = source_dataframe.copy()
    pred_values = np.asarray(predictions)
    if pred_values.ndim == 1:
        pred_values = pred_values.reshape(-1, 1)

    for index, name in enumerate(target_names):
        output[f"预测_{name}"] = pred_values[:, index]

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_excel(path, index=False)
    return path

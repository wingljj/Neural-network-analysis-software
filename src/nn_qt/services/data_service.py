"""Excel 数据读取、变量切分和预处理服务。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from nn_qt.models.data_models import (
    DatasetBundle,
    ExcelLoadConfig,
    PreprocessConfig,
    ProcessedBundle,
)


class DataService:
    """不依赖 Qt 的数据服务，便于测试和复用。"""

    def load_excel(self, config: ExcelLoadConfig) -> pd.DataFrame:
        path = Path(config.path)
        if not path.exists():
            raise FileNotFoundError(f"Excel 文件不存在: {path}")

        engine = self._select_excel_engine(path)
        df = pd.read_excel(
            path,
            sheet_name=config.sheet_name,
            header=config.header,
            engine=engine,
        )
        if df.empty:
            raise ValueError("Excel sheet 为空，无法分析")
        return df

    def split_features_targets(
        self,
        df: pd.DataFrame,
        feature_count: int,
        target_count: int,
    ) -> DatasetBundle:
        if feature_count <= 0:
            raise ValueError("feature_count 必须大于 0")
        if target_count <= 0:
            raise ValueError("target_count 必须大于 0")
        if feature_count + target_count > len(df.columns):
            raise ValueError("输入变量和输出变量的列数之和不能超过总列数")

        feature_columns = list(df.columns[:feature_count])
        target_columns = list(df.columns[-target_count:])
        feature_names = [str(column) for column in feature_columns]
        target_names = [str(column) for column in target_columns]
        X = df.loc[:, feature_columns].copy()
        y = df.loc[:, target_columns].copy()
        X.columns = feature_names
        y.columns = target_names
        return DatasetBundle(
            raw=df.copy(),
            X=X,
            y=y,
            feature_names=feature_names,
            target_names=target_names,
        )

    def preprocess(
        self,
        bundle: DatasetBundle,
        config: PreprocessConfig,
    ) -> ProcessedBundle:
        X = self._to_numeric_dataframe(bundle.X, "输入变量")
        y = self._to_numeric_dataframe(bundle.y, "目标变量")

        if y.isna().any().any():
            raise ValueError("目标变量中存在缺失值，请先清理目标列")

        X, y = self._handle_missing_values(X, y, config)
        if X.empty or y.empty:
            raise ValueError("缺失值处理后没有可用样本")
        if X.isna().any().any():
            missing_columns = [str(column) for column in X.columns[X.isna().any()]]
            raise ValueError(f"输入变量在缺失值处理后仍存在缺失值: {missing_columns}")
        scaler = None
        if config.scaler == "standard":
            scaler = StandardScaler()
        elif config.scaler == "minmax":
            scaler = MinMaxScaler()

        if scaler is not None:
            scaled_values = scaler.fit_transform(X)
            X = pd.DataFrame(scaled_values, columns=bundle.feature_names, index=X.index)

        return ProcessedBundle(
            raw=bundle.raw.copy(),
            X=X.reset_index(drop=True),
            y=y.reset_index(drop=True),
            feature_names=bundle.feature_names,
            target_names=bundle.target_names,
            scaler=scaler,
            warnings=[],
        )

    def _select_excel_engine(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".xlsx", ".xlsm"}:
            return "openpyxl"
        if suffix == ".xls":
            return "xlrd"
        raise ValueError(f"不支持的 Excel 文件格式: {suffix}")

    def _to_numeric_dataframe(self, df: pd.DataFrame, label: str) -> pd.DataFrame:
        numeric = df.copy()
        for column in numeric.columns:
            try:
                numeric[column] = pd.to_numeric(numeric[column], errors="raise")
            except Exception as exc:
                raise ValueError(f"{label}列 {column} 包含非数值数据") from exc
        return numeric.replace([np.inf, -np.inf], np.nan)

    def _handle_missing_values(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame,
        config: PreprocessConfig,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        if config.missing_strategy == "drop_rows":
            mask = ~X.isna().any(axis=1)
            return X.loc[mask].copy(), y.loc[mask].copy()
        if config.missing_strategy == "mean":
            return X.fillna(X.mean(numeric_only=True)), y
        if config.missing_strategy == "median":
            return X.fillna(X.median(numeric_only=True)), y
        if config.missing_strategy == "constant":
            value = 0.0 if config.fill_value is None else config.fill_value
            return X.fillna(value), y
        raise ValueError(f"未知缺失值处理策略: {config.missing_strategy}")

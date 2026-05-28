"""模型加载、特征对齐和 Excel 预测导出服务。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nn_qt.models.result_models import PredictionResult
from nn_qt.services.model_store import ModelStore


class PredictionService:
    """对新 Excel 数据执行预测并导出结果。"""

    def __init__(self, model_store: ModelStore | None = None) -> None:
        self.model_store = model_store or ModelStore()

    def predict_excel(
        self,
        model_path: str | Path,
        excel_path: str | Path,
        output_path: str | Path,
    ) -> PredictionResult:
        package = self.model_store.load(model_path)
        input_path = Path(excel_path)
        if not input_path.exists():
            raise FileNotFoundError(f"预测 Excel 文件不存在: {input_path}")

        engine = "xlrd" if input_path.suffix.lower() == ".xls" else "openpyxl"
        raw = pd.read_excel(input_path, engine=engine)
        missing = [column for column in package.feature_columns if column not in raw.columns]
        if missing:
            raise ValueError(f"预测文件缺少训练特征列: {missing}")

        raw_features = raw.loc[:, package.feature_columns].copy()
        for column in raw_features.columns:
            raw_features[column] = pd.to_numeric(raw_features[column], errors="raise")
        if raw_features.isna().any().any():
            raise ValueError("预测输入特征中存在缺失值")

        model_features = raw_features.copy()
        inverse_transformed_features = None
        if package.scaler is not None:
            model_features = pd.DataFrame(
                package.scaler.transform(raw_features),
                columns=package.feature_columns,
                index=raw_features.index,
            )
            inverse_transformed_features = pd.DataFrame(
                package.scaler.inverse_transform(model_features),
                columns=package.feature_columns,
                index=raw_features.index,
            )

        prediction_values = package.model.predict(model_features)
        prediction_columns = [
            f"Predicted_{target_name}" for target_name in package.target_columns
        ]
        if len(prediction_columns) == 1:
            predictions = pd.DataFrame(
                {prediction_columns[0]: prediction_values},
                index=raw.index,
            )
        else:
            predictions = pd.DataFrame(
                prediction_values,
                columns=prediction_columns,
                index=raw.index,
            )

        self._export_predictions(
            raw,
            predictions,
            package,
            Path(output_path),
            model_features=model_features if package.scaler is not None else None,
            inverse_transformed_features=inverse_transformed_features,
        )
        return PredictionResult(
            predictions=predictions,
            output_path=str(output_path),
            inverse_transformed_features=inverse_transformed_features,
        )

    def _export_predictions(
        self,
        raw: pd.DataFrame,
        predictions: pd.DataFrame,
        package,
        output_path: Path,
        model_features: pd.DataFrame | None = None,
        inverse_transformed_features: pd.DataFrame | None = None,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            pd.concat([raw, predictions], axis=1).to_excel(
                writer,
                sheet_name="Predictions",
                index=False,
            )
            if model_features is not None:
                model_features.to_excel(writer, sheet_name="ModelInputFeatures", index=False)
            if inverse_transformed_features is not None:
                inverse_transformed_features.to_excel(
                    writer,
                    sheet_name="InverseTransformedFeatures",
                    index=False,
                )
            pd.DataFrame(
                {
                    "item": [
                        "app_version",
                        "created_at",
                        "feature_columns",
                        "target_columns",
                        "train_mse",
                        "test_mse",
                    ],
                    "value": [
                        package.app_version,
                        package.created_at,
                        ", ".join(package.feature_columns),
                        ", ".join(package.target_columns),
                        package.metrics.get("train_mse"),
                        package.metrics.get("test_mse"),
                    ],
                }
            ).to_excel(writer, sheet_name="ModelInfo", index=False)

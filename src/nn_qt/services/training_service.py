"""神经网络训练服务。"""

from __future__ import annotations

from datetime import datetime
import warnings

import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor

from nn_qt.config import APP_VERSION
from nn_qt.models.data_models import ProcessedBundle
from nn_qt.models.result_models import ModelPackage, TrainResult
from nn_qt.models.train_models import TrainConfig


class TrainingService:
    """封装 MLPRegressor 训练、评估和模型包生成。"""

    def train(self, bundle: ProcessedBundle, config: TrainConfig) -> TrainResult:
        X_train, X_test, y_train, y_test = train_test_split(
            bundle.X,
            bundle.y,
            test_size=config.test_size,
            random_state=config.random_state,
        )
        y_train_fit = y_train.iloc[:, 0] if y_train.shape[1] == 1 else y_train

        model = MLPRegressor(
            hidden_layer_sizes=config.hidden_layers,
            learning_rate_init=config.learning_rate,
            max_iter=config.epochs,
            random_state=config.random_state,
            n_iter_no_change=config.epochs + 1,
            tol=0.0,
            solver="adam",
        )
        # 用户可能故意设置较小 epochs 做快速试跑，收敛警告不应打断桌面端流程。
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            model.fit(X_train, y_train_fit)

        train_pred = self._prediction_frame(
            model.predict(X_train),
            bundle.target_names,
            index=X_train.index,
        )
        test_pred = self._prediction_frame(
            model.predict(X_test),
            bundle.target_names,
            index=X_test.index,
        )
        metrics = {
            "train_mse": float(mean_squared_error(y_train, train_pred)),
            "train_r2": float(r2_score(y_train, train_pred)),
            "test_mse": float(mean_squared_error(y_test, test_pred)),
            "test_r2": float(r2_score(y_test, test_pred)),
        }
        loss_curve = [float(value) for value in getattr(model, "loss_curve_", [])]
        package = ModelPackage(
            model=model,
            scaler=bundle.scaler,
            feature_columns=bundle.feature_names,
            target_columns=bundle.target_names,
            train_config=config,
            metrics=metrics,
            loss_curve=loss_curve,
            created_at=datetime.now().isoformat(timespec="seconds"),
            app_version=APP_VERSION,
        )
        return TrainResult(
            model_package=package,
            train_mse=metrics["train_mse"],
            train_r2=metrics["train_r2"],
            test_mse=metrics["test_mse"],
            test_r2=metrics["test_r2"],
            loss_curve=loss_curve,
            y_test=y_test.reset_index(drop=True),
            y_pred=test_pred.reset_index(drop=True),
        )

    def _prediction_frame(
        self,
        values,
        target_names: list[str],
        index,
    ) -> pd.DataFrame:
        if len(target_names) == 1:
            return pd.DataFrame({target_names[0]: values}, index=index)
        return pd.DataFrame(values, columns=target_names, index=index)

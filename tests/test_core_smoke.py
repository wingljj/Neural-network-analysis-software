"""核心模块烟雾测试。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from nn_analysis_app.core.analysis import run_anova, run_pca, run_sensitivity_analysis
from nn_analysis_app.core.config import DataConfig, TrainingConfig
from nn_analysis_app.core.data_io import prepare_dataset
from nn_analysis_app.core.modeling import parse_hidden_layers, train_mlp


def make_dataframe(rows: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    x1 = rng.normal(size=rows)
    x2 = rng.normal(size=rows)
    x3 = rng.normal(size=rows)
    y = 2.5 * x1 - 0.8 * x2 + 0.2 * x3 + rng.normal(scale=0.05, size=rows)
    return pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "y": y})


def test_prepare_and_analysis_pipeline() -> None:
    dataset = prepare_dataset(make_dataframe(), DataConfig(feature_count=3, target_count=1))
    pca = run_pca(dataset.features, dataset.scaled_features)
    anova = run_anova(dataset.features, dataset.targets)
    sensitivity = run_sensitivity_analysis(
        dataset.features,
        dataset.targets,
        n_estimators=20,
        n_repeats=3,
    )

    assert pca.components.shape[1] == 2
    assert {"target", "feature", "f_value", "p_value"} <= set(anova.table.columns)
    assert sensitivity.importance_table.iloc[0]["feature"] == "x1"


def test_train_mlp_smoke() -> None:
    dataset = prepare_dataset(make_dataframe(), DataConfig(feature_count=3, target_count=1))
    result = train_mlp(
        dataset,
        TrainingConfig(hidden_layers=parse_hidden_layers("8"), epochs=20),
    )

    assert "mse" in result.metrics
    assert len(result.bundle.feature_names) == 3

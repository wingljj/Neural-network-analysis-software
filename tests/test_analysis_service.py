import pandas as pd

from nn_qt.models.data_models import PreprocessConfig
from nn_qt.services.analysis_service import AnalysisService
from nn_qt.services.data_service import DataService


def _processed_bundle():
    df = pd.DataFrame(
        {
            "x1": [1, 2, 3, 4, 5, 6],
            "x2": [6, 5, 4, 3, 2, 1],
            "y": [2, 4, 6, 8, 10, 12],
        }
    )
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)
    return DataService().preprocess(
        bundle,
        PreprocessConfig(missing_strategy="mean", scaler="standard"),
    )


def test_pca_returns_two_components_and_variance_ratio():
    result = AnalysisService().run_pca(_processed_bundle(), n_components=2)

    assert result.components.shape == (6, 2)
    assert len(result.explained_variance_ratio) == 2


def test_anova_returns_target_by_feature_tables():
    result = AnalysisService().run_anova(_processed_bundle())

    assert list(result.f_values.columns) == ["x1", "x2"]
    assert list(result.f_values.index) == ["y"]
    assert list(result.p_values.columns) == ["x1", "x2"]


def test_sensitivity_returns_feature_importance_rows():
    result = AnalysisService().run_sensitivity(_processed_bundle(), random_state=7)

    assert set(result.importance.columns) == {"feature", "importance"}
    assert set(result.importance["feature"]) == {"x1", "x2"}

import numpy as np
import pandas as pd
import pytest

from nn_qt.models.data_models import ExcelLoadConfig, PreprocessConfig
from nn_qt.services.data_service import DataService


def test_split_features_targets_uses_front_n_and_back_m_columns():
    df = pd.DataFrame({"x1": [1, 2], "x2": [3, 4], "y": [5, 6]})

    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)

    assert bundle.feature_names == ["x1", "x2"]
    assert bundle.target_names == ["y"]
    assert bundle.X.shape == (2, 2)
    assert bundle.y.shape == (2, 1)


def test_split_features_targets_by_names_allows_explicit_column_roles():
    df = pd.DataFrame(
        {
            "sample_id": ["A", "B"],
            "temp": [20.0, 25.0],
            "pressure": [1.1, 1.3],
            "strength": [300.0, 320.0],
            "yield": [0.82, 0.85],
        }
    )

    bundle = DataService().split_features_targets_by_names(
        df,
        feature_columns=["temp", "pressure"],
        target_columns=["strength"],
    )

    assert bundle.feature_names == ["temp", "pressure"]
    assert bundle.target_names == ["strength"]
    assert list(bundle.X.columns) == ["temp", "pressure"]
    assert list(bundle.y.columns) == ["strength"]
    assert bundle.X.shape == (2, 2)
    assert bundle.y.shape == (2, 1)


def test_split_features_targets_by_names_rejects_invalid_column_roles():
    df = pd.DataFrame({"x1": [1.0], "x2": [2.0], "y": [3.0]})
    service = DataService()

    with pytest.raises(ValueError, match="至少选择一个输入变量"):
        service.split_features_targets_by_names(df, [], ["y"])

    with pytest.raises(ValueError, match="至少选择一个输出变量"):
        service.split_features_targets_by_names(df, ["x1"], [])

    with pytest.raises(ValueError, match="不能同时作为输入和输出"):
        service.split_features_targets_by_names(df, ["x1"], ["x1"])

    with pytest.raises(ValueError, match="不存在"):
        service.split_features_targets_by_names(df, ["x1", "missing"], ["y"])


def test_split_features_targets_rejects_invalid_column_counts():
    df = pd.DataFrame({"x1": [1], "y": [2]})

    with pytest.raises(ValueError, match="feature_count"):
        DataService().split_features_targets(df, feature_count=0, target_count=1)

    with pytest.raises(ValueError, match="列数"):
        DataService().split_features_targets(df, feature_count=2, target_count=1)


def test_preprocess_mean_fills_feature_missing_values_and_scales():
    df = pd.DataFrame(
        {
            "x1": [1.0, np.nan, 3.0],
            "x2": [2.0, 4.0, 6.0],
            "y": [1.0, 2.0, 3.0],
        }
    )
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)

    processed = DataService().preprocess(
        bundle,
        PreprocessConfig(missing_strategy="mean", scaler="standard"),
    )

    assert not processed.X.isna().any().any()
    assert processed.scaler is not None
    assert processed.X.shape == (3, 2)


def test_preprocess_rejects_missing_target_values():
    df = pd.DataFrame({"x1": [1.0, 2.0], "y": [1.0, np.nan]})
    bundle = DataService().split_features_targets(df, feature_count=1, target_count=1)

    with pytest.raises(ValueError, match="目标变量"):
        DataService().preprocess(bundle, PreprocessConfig(missing_strategy="mean", scaler="none"))


def test_preprocess_rejects_feature_columns_that_remain_missing_after_mean_fill():
    df = pd.DataFrame({"x1": [np.nan, np.nan], "y": [1.0, 2.0]})
    bundle = DataService().split_features_targets(df, feature_count=1, target_count=1)

    with pytest.raises(ValueError, match="仍存在缺失值"):
        DataService().preprocess(bundle, PreprocessConfig(missing_strategy="mean", scaler="none"))


def test_preprocess_rejects_drop_rows_when_no_samples_remain():
    df = pd.DataFrame({"x1": [np.nan, np.nan], "y": [1.0, 2.0]})
    bundle = DataService().split_features_targets(df, feature_count=1, target_count=1)

    with pytest.raises(ValueError, match="没有可用样本"):
        DataService().preprocess(bundle, PreprocessConfig(missing_strategy="drop_rows", scaler="none"))


def test_load_excel_reads_xlsx_file(tmp_path):
    path = tmp_path / "sample.xlsx"
    pd.DataFrame({"x": [1], "y": [2]}).to_excel(path, index=False)

    df = DataService().load_excel(
        ExcelLoadConfig(path=str(path), feature_count=1, target_count=1)
    )

    assert list(df.columns) == ["x", "y"]

import pytest

from nn_qt.config import APP_NAME, APP_VERSION
from nn_qt.models.data_models import ExcelLoadConfig, PreprocessConfig
from nn_qt.models.train_models import TrainConfig, parse_hidden_layers


def test_app_metadata_is_defined():
    assert APP_NAME == "数据分析与神经网络预测"
    assert APP_VERSION == "0.1.0"


def test_config_dataclasses_keep_user_choices():
    excel = ExcelLoadConfig(path="demo.xlsx", feature_count=3, target_count=1)
    preprocess = PreprocessConfig(missing_strategy="mean", scaler="standard")

    assert excel.feature_count == 3
    assert excel.target_count == 1
    assert preprocess.scaler == "standard"


def test_parse_hidden_layers_accepts_comma_separated_nodes():
    assert parse_hidden_layers("64, 32") == (64, 32)


def test_train_config_rejects_invalid_learning_rate():
    with pytest.raises(ValueError, match="learning_rate"):
        TrainConfig(hidden_layers=(8,), learning_rate=0, epochs=10)

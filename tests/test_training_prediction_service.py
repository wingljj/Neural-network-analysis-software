import pandas as pd

from nn_qt.models.data_models import PreprocessConfig
from nn_qt.models.train_models import TrainConfig
from nn_qt.services.data_service import DataService
from nn_qt.services.model_store import ModelStore
from nn_qt.services.prediction_service import PredictionService
from nn_qt.services.training_service import TrainingService


def _processed_bundle():
    df = pd.DataFrame(
        {
            "x1": list(range(20)),
            "x2": list(range(20, 40)),
            "y": [value * 2.0 for value in range(20)],
        }
    )
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)
    return DataService().preprocess(
        bundle,
        PreprocessConfig(missing_strategy="mean", scaler="standard"),
    )


def test_training_outputs_metrics_and_loss_curve():
    result = TrainingService().train(
        _processed_bundle(),
        TrainConfig(hidden_layers=(8,), learning_rate=0.01, epochs=30, random_state=3),
    )

    assert result.test_mse >= 0
    assert isinstance(result.test_r2, float)
    assert len(result.loss_curve) > 0
    assert result.model_package.feature_columns == ["x1", "x2"]


def test_saved_model_can_predict_excel_and_export(tmp_path):
    processed = _processed_bundle()
    result = TrainingService().train(
        processed,
        TrainConfig(hidden_layers=(8,), learning_rate=0.01, epochs=30, random_state=3),
    )
    model_path = tmp_path / "model.joblib"
    ModelStore().save(result.model_package, model_path)
    input_path = tmp_path / "predict.xlsx"
    output_path = tmp_path / "predictions.xlsx"
    pd.DataFrame({"x2": [22, 25], "x1": [2, 5]}).to_excel(input_path, index=False)

    prediction = PredictionService().predict_excel(model_path, input_path, output_path)

    assert prediction.predictions.shape == (2, 1)
    assert list(prediction.predictions.columns) == ["Predicted_y"]
    assert prediction.inverse_transformed_features is not None
    pd.testing.assert_frame_equal(
        prediction.inverse_transformed_features.reset_index(drop=True),
        pd.DataFrame({"x1": [2, 5], "x2": [22, 25]}),
        check_dtype=False,
    )
    inverse_sheet = pd.read_excel(output_path, sheet_name="InverseTransformedFeatures")
    pd.testing.assert_frame_equal(
        inverse_sheet,
        pd.DataFrame({"x1": [2, 5], "x2": [22, 25]}),
        check_dtype=False,
    )
    assert output_path.exists()

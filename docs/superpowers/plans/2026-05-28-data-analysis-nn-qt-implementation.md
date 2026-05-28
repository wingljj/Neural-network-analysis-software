# 数据分析与神经网络预测 Qt 软件 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable PySide2/Qt 5.15 desktop skeleton with tested data analysis, MLP training, model persistence, prediction export, and packaging scaffolding.

**Architecture:** The UI layer only collects parameters and renders state. Data processing, analysis, training, persistence, and prediction live in pure Python service modules so they can be tested without Qt. Long-running UI actions are represented by worker classes that can later move to QThread.

**Tech Stack:** Python 3.10+, PySide2, pandas, numpy, scikit-learn, matplotlib, joblib, openpyxl, xlrd, xlsxwriter, pytest, PyInstaller.

---

## File Map

- `requirements.txt`: runtime dependencies.
- `requirements-dev.txt`: development, testing, packaging dependencies.
- `pyproject.toml`: pytest configuration and package metadata.
- `README.md`: usage and packaging notes.
- `src/nn_qt/__main__.py`: `python -m nn_qt` entry.
- `src/nn_qt/app.py`: QApplication creation and app startup.
- `src/nn_qt/config.py`: app constants.
- `src/nn_qt/models/*.py`: dataclasses for configs and results.
- `src/nn_qt/services/data_service.py`: Excel loading, N/M splitting, missing value handling, scaling.
- `src/nn_qt/services/analysis_service.py`: PCA, ANOVA, sensitivity analysis.
- `src/nn_qt/services/training_service.py`: MLPRegressor training and metrics.
- `src/nn_qt/services/model_store.py`: joblib save/load model packages.
- `src/nn_qt/services/prediction_service.py`: model loading, feature alignment, Excel prediction export.
- `src/nn_qt/ui/*.py`: Qt widgets and pages.
- `src/nn_qt/workers/*.py`: worker objects for training and prediction.
- `tests/*.py`: pytest coverage for services and smoke import/UI behavior.
- `packaging/*.ps1`, `packaging/nn_qt.spec`: offline package scaffolding.

## Task 1: Project Metadata And Domain Models

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/nn_qt/__init__.py`
- Create: `src/nn_qt/config.py`
- Create: `src/nn_qt/models/data_models.py`
- Create: `src/nn_qt/models/train_models.py`
- Create: `src/nn_qt/models/result_models.py`
- Test: `tests/test_models_and_config.py`

- [ ] **Step 1: Write the failing test**

```python
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
    try:
        TrainConfig(hidden_layers=(8,), learning_rate=0, epochs=10)
    except ValueError as exc:
        assert "learning_rate" in str(exc)
    else:
        raise AssertionError("TrainConfig should reject non-positive learning rate")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models_and_config.py -v`

Expected: FAIL because `nn_qt` package and dataclasses do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create constants, dataclasses, and validation helpers exactly matching the test expectations. Use `__post_init__` for parameter validation and keep comments in Chinese where domain rules may surprise users.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models_and_config.py -v`

Expected: PASS.

## Task 2: Data Loading And Preprocessing Service

**Files:**
- Create: `src/nn_qt/services/data_service.py`
- Modify: `src/nn_qt/models/data_models.py`
- Test: `tests/test_data_service.py`

- [ ] **Step 1: Write the failing test**

```python
import numpy as np
import pandas as pd

from nn_qt.models.data_models import ExcelLoadConfig, PreprocessConfig
from nn_qt.services.data_service import DataService


def test_split_features_targets_uses_front_n_and_back_m_columns():
    df = pd.DataFrame({"x1": [1, 2], "x2": [3, 4], "y": [5, 6]})
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)
    assert bundle.feature_names == ["x1", "x2"]
    assert bundle.target_names == ["y"]
    assert bundle.X.shape == (2, 2)
    assert bundle.y.shape == (2, 1)


def test_preprocess_mean_fills_feature_missing_values_and_scales():
    df = pd.DataFrame({"x1": [1.0, np.nan, 3.0], "x2": [2.0, 4.0, 6.0], "y": [1.0, 2.0, 3.0]})
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)
    processed = DataService().preprocess(bundle, PreprocessConfig(missing_strategy="mean", scaler="standard"))
    assert not processed.X.isna().any().any()
    assert processed.scaler is not None
    assert processed.X.shape == (3, 2)


def test_load_excel_reads_xlsx_file(tmp_path):
    path = tmp_path / "sample.xlsx"
    pd.DataFrame({"x": [1], "y": [2]}).to_excel(path, index=False)
    df = DataService().load_excel(ExcelLoadConfig(path=str(path), feature_count=1, target_count=1))
    assert list(df.columns) == ["x", "y"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_data_service.py -v`

Expected: FAIL because `DataService` is missing.

- [ ] **Step 3: Write minimal implementation**

Implement Excel engine selection, column count validation, numeric conversion, missing value handling, and optional StandardScaler/MinMaxScaler.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_data_service.py -v`

Expected: PASS.

## Task 3: Statistical Analysis Service

**Files:**
- Create: `src/nn_qt/services/analysis_service.py`
- Modify: `src/nn_qt/models/result_models.py`
- Test: `tests/test_analysis_service.py`

- [ ] **Step 1: Write the failing test**

```python
import pandas as pd

from nn_qt.models.data_models import PreprocessConfig
from nn_qt.services.analysis_service import AnalysisService
from nn_qt.services.data_service import DataService


def _processed_bundle():
    df = pd.DataFrame({
        "x1": [1, 2, 3, 4, 5, 6],
        "x2": [6, 5, 4, 3, 2, 1],
        "y": [2, 4, 6, 8, 10, 12],
    })
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)
    return DataService().preprocess(bundle, PreprocessConfig(missing_strategy="mean", scaler="standard"))


def test_pca_returns_two_components_and_variance_ratio():
    result = AnalysisService().run_pca(_processed_bundle(), n_components=2)
    assert result.components.shape == (6, 2)
    assert len(result.explained_variance_ratio) == 2


def test_anova_returns_target_by_feature_tables():
    result = AnalysisService().run_anova(_processed_bundle())
    assert list(result.f_values.columns) == ["x1", "x2"]
    assert list(result.f_values.index) == ["y"]


def test_sensitivity_returns_feature_importance_rows():
    result = AnalysisService().run_sensitivity(_processed_bundle(), random_state=7)
    assert set(result.importance.columns) == {"feature", "importance"}
    assert set(result.importance["feature"]) == {"x1", "x2"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analysis_service.py -v`

Expected: FAIL because `AnalysisService` is missing.

- [ ] **Step 3: Write minimal implementation**

Implement PCA, per-target `f_regression`, and RandomForestRegressor feature importance.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analysis_service.py -v`

Expected: PASS.

## Task 4: Training, Model Store, And Prediction Service

**Files:**
- Create: `src/nn_qt/services/training_service.py`
- Create: `src/nn_qt/services/model_store.py`
- Create: `src/nn_qt/services/prediction_service.py`
- Modify: `src/nn_qt/models/train_models.py`
- Modify: `src/nn_qt/models/result_models.py`
- Test: `tests/test_training_prediction_service.py`

- [ ] **Step 1: Write the failing test**

```python
import pandas as pd

from nn_qt.models.data_models import PreprocessConfig
from nn_qt.models.train_models import TrainConfig
from nn_qt.services.data_service import DataService
from nn_qt.services.model_store import ModelStore
from nn_qt.services.prediction_service import PredictionService
from nn_qt.services.training_service import TrainingService


def _processed_bundle():
    df = pd.DataFrame({
        "x1": list(range(20)),
        "x2": list(range(20, 40)),
        "y": [v * 2.0 for v in range(20)],
    })
    bundle = DataService().split_features_targets(df, feature_count=2, target_count=1)
    return DataService().preprocess(bundle, PreprocessConfig(missing_strategy="mean", scaler="standard"))


def test_training_outputs_metrics_and_loss_curve():
    result = TrainingService().train(
        _processed_bundle(),
        TrainConfig(hidden_layers=(8,), learning_rate=0.01, epochs=30, random_state=3),
    )
    assert result.test_mse >= 0
    assert isinstance(result.test_r2, float)
    assert len(result.loss_curve) > 0


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
    assert output_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_training_prediction_service.py -v`

Expected: FAIL because training, model store, and prediction services are missing.

- [ ] **Step 3: Write minimal implementation**

Implement train/test split, MLPRegressor, metrics, model package persistence, feature alignment, prediction, and Excel export.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_training_prediction_service.py -v`

Expected: PASS.

## Task 5: Qt Application Skeleton

**Files:**
- Create: `src/nn_qt/__main__.py`
- Create: `src/nn_qt/app.py`
- Create: `src/nn_qt/ui/main_window.py`
- Create: `src/nn_qt/ui/sidebar.py`
- Create: `src/nn_qt/ui/log_panel.py`
- Create: `src/nn_qt/ui/chart_widget.py`
- Create: `src/nn_qt/ui/data_page.py`
- Create: `src/nn_qt/ui/analysis_page.py`
- Create: `src/nn_qt/ui/train_page.py`
- Create: `src/nn_qt/ui/predict_page.py`
- Create: `src/nn_qt/workers/train_worker.py`
- Create: `src/nn_qt/workers/predict_worker.py`
- Test: `tests/test_qt_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide2.QtWidgets import QApplication

from nn_qt.ui.main_window import MainWindow


def test_main_window_can_be_created():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    assert window.windowTitle() == "数据分析与神经网络预测"
    assert window.sidebar.count() >= 4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_qt_smoke.py -v`

Expected: FAIL because Qt UI modules are missing.

- [ ] **Step 3: Write minimal implementation**

Create a styled QMainWindow with sidebar navigation, stacked pages, log panel, parameter fields, buttons, placeholder chart canvases, and worker classes exposing Qt signals.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_qt_smoke.py -v`

Expected: PASS when PySide2 is installed; otherwise SKIP with a clear message.

## Task 6: Packaging Scripts And Full Verification

**Files:**
- Create: `packaging/nn_qt.spec`
- Create: `packaging/build.ps1`
- Create: `packaging/build_offline.ps1`
- Create: `packaging/prepare_wheels.ps1`
- Create: `packaging/smoke_test.ps1`
- Modify: `README.md`

- [ ] **Step 1: Add packaging scaffold**

Create PowerShell scripts for wheel preparation, local build, offline build, and executable smoke test. The spec should use onedir mode and include Qt resources, hidden imports, and package data.

- [ ] **Step 2: Run service tests**

Run: `pytest tests/test_models_and_config.py tests/test_data_service.py tests/test_analysis_service.py tests/test_training_prediction_service.py -v`

Expected: PASS.

- [ ] **Step 3: Run Qt smoke test**

Run: `pytest tests/test_qt_smoke.py -v`

Expected: PASS if PySide2 is installed, SKIP if Qt dependencies are absent.

- [ ] **Step 4: Run all tests**

Run: `pytest -v`

Expected: PASS or Qt-only SKIP in environments without PySide2.

## Self-Review

Spec coverage:

- Qt main window, sidebar, pages, log panel, and chart area are covered by Task 5.
- Excel import, N/M split, missing values, and scaling are covered by Task 2.
- PCA, ANOVA, and sensitivity analysis are covered by Task 3.
- MLP training, metrics, loss curve, model save/load, prediction, and Excel export are covered by Task 4.
- Offline package scaffolding is covered by Task 6.

Placeholder scan:

- The plan contains no `TBD`, `TODO`, or "implement later" markers.

Type consistency:

- `ExcelLoadConfig`, `PreprocessConfig`, `TrainConfig`, `DatasetBundle`, `ProcessedBundle`, `TrainResult`, and model package names are consistent across tasks.

import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_compat = pytest.importorskip("nn_qt.qt_compat")
QtWidgets = qt_compat.QtWidgets
from nn_qt.ui.main_window import MainWindow


def _app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_main_window_can_be_created():
    app = _app()

    window = MainWindow()

    assert app is not None
    assert window.windowTitle() == "数据分析与神经网络预测"
    assert window.sidebar.count() >= 5


def test_sidebar_exposes_machine_learning_preprocess_page():
    app = _app()
    assert app is not None
    window = MainWindow()
    labels = [window.sidebar.item(index).text() for index in range(window.sidebar.count())]

    assert labels == ["数据导入", "机器学习预处理", "统计分析", "模型训练", "预测导出"]
    assert window.stack.count() == window.sidebar.count()
    assert window.stack.widget(1) is window.ml_preprocess_page


def test_main_window_import_signal_loads_and_preprocesses_excel(tmp_path):
    app = _app()
    assert app is not None
    path = tmp_path / "data.xlsx"
    pd.DataFrame({"x1": [1.0, None, 3.0], "x2": [2.0, 4.0, 6.0], "y": [3.0, 6.0, 9.0]}).to_excel(
        path,
        index=False,
    )
    window = MainWindow()

    window.data_page.import_requested.emit(str(path))

    assert window.dataset_bundle is not None
    assert window.processed_bundle is not None
    assert window.data_page.preview.rowCount() == 3
    assert window.data_page.column_roles.rowCount() == 3
    assert window.data_page.selected_feature_target_columns() == (["x1", "x2"], ["y"])
    assert "数据导入完成" in window.log_panel.output.toPlainText()


def test_data_import_and_ml_preprocess_controls_are_separated():
    app = _app()
    assert app is not None
    window = MainWindow()

    assert not hasattr(window.data_page, "feature_count")
    assert not hasattr(window.data_page, "target_count")
    assert not hasattr(window.data_page, "missing_strategy")
    assert not hasattr(window.data_page, "scaler")
    assert not hasattr(window.data_page, "fill_value")
    assert hasattr(window.data_page, "column_roles")
    assert hasattr(window.data_page, "apply_columns_button")
    assert window.ml_preprocess_page.missing_strategy.count() >= 3
    assert window.ml_preprocess_page.scaler.count() >= 3
    assert window.ml_preprocess_page.fill_value.value() == 0.0
    assert window.train_page.test_size.value() == 0.2


def test_column_roles_can_be_changed_after_import(tmp_path):
    app = _app()
    assert app is not None
    path = tmp_path / "data.xlsx"
    pd.DataFrame({"x1": [1.0, 2.0], "x2": [3.0, 4.0], "y": [5.0, 6.0]}).to_excel(
        path,
        index=False,
    )
    window = MainWindow()
    window.data_page.import_requested.emit(str(path))

    window.data_page.set_column_role("x1", "输出变量")
    window.data_page.set_column_role("x2", "输入变量")
    window.data_page.set_column_role("y", "忽略")
    window.data_page.apply_columns_button.click()

    assert window.dataset_bundle is not None
    assert window.processed_bundle is not None
    assert window.dataset_bundle.feature_names == ["x2"]
    assert window.dataset_bundle.target_names == ["x1"]
    assert window.processed_bundle.feature_names == ["x2"]
    assert window.processed_bundle.target_names == ["x1"]
    assert "变量设置已应用" in window.log_panel.output.toPlainText()


def test_machine_learning_preprocess_page_reprocesses_imported_dataset(tmp_path):
    app = _app()
    assert app is not None
    path = tmp_path / "data.xlsx"
    pd.DataFrame({"x1": [1.0, None, 5.0], "x2": [2.0, 4.0, 6.0], "y": [3.0, 6.0, 9.0]}).to_excel(
        path,
        index=False,
    )
    window = MainWindow()
    window.data_page.import_requested.emit(str(path))

    window.ml_preprocess_page.missing_strategy.setCurrentText("median")
    window.ml_preprocess_page.scaler.setCurrentText("minmax")
    window.ml_preprocess_page.test_size.setValue(0.3)
    window.ml_preprocess_page.random_state.setValue(7)
    window.ml_preprocess_page.apply_button.click()

    assert window.processed_bundle is not None
    assert window.processed_bundle.X.min().min() >= 0.0
    assert window.processed_bundle.X.max().max() <= 1.0
    assert window.train_page.test_size.value() == 0.3
    assert window._ml_random_state == 7
    assert "机器学习预处理已应用" in window.log_panel.output.toPlainText()

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_compat = pytest.importorskip("nn_qt.qt_compat")
QtWidgets = qt_compat.QtWidgets

from nn_qt.ui.main_window import MainWindow
from nn_qt.ui.predict_page import PredictPage


def _app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_predict_page_file_buttons_fill_paths(monkeypatch, tmp_path):
    app = _app()
    assert app is not None
    page = PredictPage()
    model_path = str(tmp_path / "model.joblib")
    input_path = str(tmp_path / "input.xlsx")
    output_path = str(tmp_path / "chosen_output.xlsx")

    responses = iter([(model_path, ""), (input_path, ""), (output_path, "")])
    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: next(responses),
    )
    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (output_path, ""),
    )

    page.choose_model_file()
    page.choose_input_file()
    page.choose_output_file()

    assert page.model_path.text() == model_path
    assert page.input_path.text() == input_path
    assert page.output_path.text() == output_path


def test_predict_input_selection_auto_fills_output_path(monkeypatch, tmp_path):
    app = _app()
    assert app is not None
    page = PredictPage()
    input_path = tmp_path / "新数据.xlsx"

    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(input_path), ""),
    )

    page.choose_input_file()

    assert page.output_path.text() == str(tmp_path / "新数据_predictions.xlsx")


def test_predict_input_selection_updates_previous_auto_output_path(monkeypatch, tmp_path):
    app = _app()
    assert app is not None
    page = PredictPage()
    first = tmp_path / "A.xlsx"
    second = tmp_path / "B.xlsx"
    responses = iter([(str(first), ""), (str(second), "")])
    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: next(responses),
    )

    page.choose_input_file()
    page.choose_input_file()

    assert page.output_path.text() == str(tmp_path / "B_predictions.xlsx")


def test_save_model_backfills_predict_page_model_path(monkeypatch, tmp_path):
    app = _app()
    assert app is not None
    window = MainWindow()
    model_path = str(tmp_path / "trained_model.joblib")
    saved_paths = []
    window.train_result = SimpleNamespace(model_package=object())
    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (model_path, ""),
    )
    monkeypatch.setattr(
        window.model_store,
        "save",
        lambda package, path: saved_paths.append(str(path)),
    )

    window._handle_save_model_requested()

    assert saved_paths == [model_path]
    assert window.predict_page.model_path.text() == model_path


def test_save_model_defaults_to_imported_data_folder(monkeypatch, tmp_path):
    app = _app()
    assert app is not None
    window = MainWindow()
    data_dir = tmp_path / "datasets"
    data_dir.mkdir()
    window._last_data_path = str(data_dir / "train.xlsx")
    window.train_result = SimpleNamespace(model_package=object())
    captured_defaults = []

    def fake_get_save_file_name(*args, **kwargs):
        captured_defaults.append(args[2])
        return "", ""

    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getSaveFileName",
        fake_get_save_file_name,
    )

    window._handle_save_model_requested()

    assert captured_defaults
    assert os.path.dirname(captured_defaults[0]) == str(data_dir)

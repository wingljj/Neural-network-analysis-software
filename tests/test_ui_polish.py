import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_compat = pytest.importorskip("nn_qt.qt_compat")
QtGui = qt_compat.QtGui
QtWidgets = qt_compat.QtWidgets

from nn_qt.app import create_application
from nn_qt.ui.main_window import MainWindow


def test_application_font_is_readable_and_sidebar_adapts_to_text():
    app = create_application([])
    window = MainWindow()

    assert app.font().pointSize() >= 11
    longest = max(
        window.sidebar.item(index).text() for index in range(window.sidebar.count())
    )
    metrics = QtGui.QFontMetrics(window.sidebar.font())

    assert window.sidebar.font().pointSize() >= 12
    assert window.sidebar.horizontalScrollBarPolicy() == qt_compat.QtCore.Qt.ScrollBarAlwaysOff
    assert window.sidebar.minimumWidth() >= metrics.horizontalAdvance(longest) + 56
    assert window.sidebar.sizeHintForRow(0) >= metrics.height() + 18


def test_main_window_uses_white_theme_tokens():
    create_application([])
    window = MainWindow()
    stylesheet = window.styleSheet().lower()

    assert "#ffffff" in stylesheet
    assert "#1f2937" not in stylesheet
    assert "qlistwidget#sidebar" in stylesheet
    assert "qlineedit" in stylesheet
    assert "qtablewidget" in stylesheet

"""统一的 Qt 白色主题和字体策略。"""

from __future__ import annotations

from nn_qt.qt_compat import QtCore, QtGui, QtWidgets


BASE_FONT_SIZE = 11
SIDEBAR_FONT_SIZE = 12
SIDEBAR_EXTRA_PADDING = 56
SIDEBAR_MIN_WIDTH = 220
SIDEBAR_MIN_ROW_HEIGHT = 52


def configure_application_font(app: QtWidgets.QApplication | None) -> None:
    """设置全局字体，避免系统默认字号过小。"""

    if app is None:
        return
    font = QtGui.QFont("Microsoft YaHei UI")
    font.setPointSize(BASE_FONT_SIZE)
    app.setFont(font)


def configure_sidebar_font(widget: QtWidgets.QListWidget) -> None:
    """单独放大侧边栏字号，保证导航文字在缩放窗口时仍清晰。"""

    font = QtGui.QFont(widget.font())
    font.setPointSize(max(font.pointSize(), SIDEBAR_FONT_SIZE))
    font.setWeight(QtGui.QFont.DemiBold)
    widget.setFont(font)


def sidebar_width_for(widget: QtWidgets.QListWidget) -> int:
    metrics = QtGui.QFontMetrics(widget.font())
    longest = ""
    for index in range(widget.count()):
        text = widget.item(index).text()
        if len(text) > len(longest):
            longest = text
    return max(SIDEBAR_MIN_WIDTH, metrics.horizontalAdvance(longest) + SIDEBAR_EXTRA_PADDING)


def sidebar_row_height_for(widget: QtWidgets.QListWidget) -> int:
    metrics = QtGui.QFontMetrics(widget.font())
    return max(SIDEBAR_MIN_ROW_HEIGHT, metrics.height() + 20)


def refresh_sidebar_metrics(widget: QtWidgets.QListWidget) -> None:
    width = sidebar_width_for(widget)
    row_height = sidebar_row_height_for(widget)
    widget.setMinimumWidth(width)
    widget.setMaximumWidth(width + 80)
    for index in range(widget.count()):
        widget.item(index).setSizeHint(QtCore.QSize(width, row_height))


def white_theme_stylesheet() -> str:
    return """
    QMainWindow, QWidget {
        background: #ffffff;
        color: #1f2933;
        selection-background-color: #dceafe;
        selection-color: #0f172a;
    }
    QSplitter::handle {
        background: #edf1f5;
    }
    QListWidget#sidebar {
        background: #ffffff;
        color: #263238;
        border-right: 1px solid #d8dee6;
        font-weight: 600;
        outline: 0;
    }
    QListWidget#sidebar::item {
        padding-left: 18px;
        padding-right: 14px;
        border-left: 4px solid transparent;
    }
    QListWidget#sidebar::item:hover {
        background: #f4f8ff;
    }
    QListWidget#sidebar::item:selected {
        background: #eaf2ff;
        color: #0f4c81;
        border-left: 4px solid #2f6fed;
    }
    QPushButton {
        min-height: 36px;
        padding: 6px 14px;
        border: 1px solid #c9d2dc;
        border-radius: 4px;
        background: #ffffff;
        color: #1f2933;
    }
    QPushButton:hover {
        background: #f5f9ff;
        border-color: #8bb7f0;
    }
    QPushButton:pressed {
        background: #eaf2ff;
    }
    QPushButton:disabled {
        color: #9aa5b1;
        background: #f3f5f7;
    }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        min-height: 32px;
        border: 1px solid #cfd8e3;
        border-radius: 4px;
        background: #ffffff;
        padding: 4px 8px;
    }
    QLineEdit:read-only {
        background: #f8fafc;
        color: #334155;
    }
    QTableWidget {
        background: #ffffff;
        alternate-background-color: #f8fafc;
        gridline-color: #e1e7ef;
        border: 1px solid #d8dee6;
        selection-background-color: #eaf2ff;
        selection-color: #0f172a;
    }
    QHeaderView::section {
        background: #f5f7fa;
        color: #334155;
        padding: 7px 8px;
        border: 0;
        border-bottom: 1px solid #d8dee6;
    }
    QStatusBar {
        background: #ffffff;
        border-top: 1px solid #e1e7ef;
    }
    """

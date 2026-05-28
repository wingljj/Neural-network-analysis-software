"""Qt 应用启动入口。"""

from __future__ import annotations

import sys

from nn_qt.config import APP_NAME, ORGANIZATION_NAME
from nn_qt.qt_compat import QtCore, QtWidgets
from nn_qt.ui.main_window import MainWindow
from nn_qt.ui.theme import configure_application_font


def create_application(argv: list[str] | None = None) -> QtWidgets.QApplication:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(argv or [])
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    configure_application_font(app)
    return app


def main(argv: list[str] | None = None) -> int:
    app = create_application(argv or sys.argv)
    window = MainWindow()
    window.resize(1280, 820)
    window.show()
    return app.exec_()

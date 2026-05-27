"""应用启动入口。"""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from nn_analysis_app.ui.main_window import MainWindow


def main() -> int:
    """创建 Qt 应用并进入事件循环。"""
    app = QApplication(sys.argv)
    app.setApplicationName("数据分析与神经网络预测")
    app.setOrganizationName("Neural Network Analysis Software")

    window = MainWindow()
    window.show()
    return app.exec_()

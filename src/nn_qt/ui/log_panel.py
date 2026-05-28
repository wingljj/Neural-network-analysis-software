"""运行日志面板。"""

from __future__ import annotations

from datetime import datetime

from nn_qt.qt_compat import QtWidgets


class LogPanel(QtWidgets.QWidget):
    """集中展示导入、分析、训练和预测过程日志。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("运行日志")
        clear_button = QtWidgets.QPushButton("清空")
        clear_button.clicked.connect(self.clear)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(clear_button)

        self.output = QtWidgets.QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(2000)
        layout.addLayout(header)
        layout.addWidget(self.output)

    def append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output.appendPlainText(f"[{timestamp}] {message}")

    def clear(self) -> None:
        self.output.clear()

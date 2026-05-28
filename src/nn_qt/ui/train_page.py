"""模型训练页面。"""

from __future__ import annotations

from nn_qt.qt_compat import Signal, QtWidgets
from nn_qt.ui.chart_widget import ChartWidget


class TrainPage(QtWidgets.QWidget):
    """神经网络训练参数配置。"""

    train_requested = Signal(str, float, int, float)
    save_model_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.hidden_layers = QtWidgets.QLineEdit("64,32")
        self.learning_rate = QtWidgets.QDoubleSpinBox()
        self.learning_rate.setDecimals(5)
        self.learning_rate.setRange(0.00001, 10.0)
        self.learning_rate.setValue(0.001)
        self.epochs = QtWidgets.QSpinBox()
        self.epochs.setRange(1, 100000)
        self.epochs.setValue(300)
        self.test_size = QtWidgets.QDoubleSpinBox()
        self.test_size.setDecimals(2)
        self.test_size.setSingleStep(0.05)
        self.test_size.setRange(0.05, 0.8)
        self.test_size.setValue(0.2)
        form.addRow("隐藏层节点", self.hidden_layers)
        form.addRow("学习率", self.learning_rate)
        form.addRow("Epochs", self.epochs)
        form.addRow("测试集比例", self.test_size)

        button_row = QtWidgets.QHBoxLayout()
        train_button = QtWidgets.QPushButton("开始训练")
        self.save_button = QtWidgets.QPushButton("保存模型")
        self.save_button.setEnabled(False)
        train_button.clicked.connect(self._emit_train_requested)
        self.save_button.clicked.connect(self.save_model_requested.emit)
        button_row.addWidget(train_button)
        button_row.addWidget(self.save_button)
        button_row.addStretch(1)

        self.metrics = QtWidgets.QTextEdit()
        self.metrics.setReadOnly(True)
        self.chart = ChartWidget()
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.metrics, stretch=1)
        layout.addWidget(self.chart, stretch=2)

    def _emit_train_requested(self) -> None:
        self.train_requested.emit(
            self.hidden_layers.text(),
            self.learning_rate.value(),
            self.epochs.value(),
            self.test_size.value(),
        )

    def set_save_enabled(self, enabled: bool) -> None:
        self.save_button.setEnabled(enabled)

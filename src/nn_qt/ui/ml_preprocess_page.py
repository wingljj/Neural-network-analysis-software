"""机器学习建模前的数据预处理页面。"""

from __future__ import annotations

from nn_qt.qt_compat import Signal, QtWidgets


class MlPreprocessPage(QtWidgets.QWidget):
    """集中配置机器学习训练前常用的数据预处理参数。"""

    preprocess_requested = Signal(str, str, float, float, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.missing_strategy = QtWidgets.QComboBox()
        self.missing_strategy.addItems(["mean", "median", "drop_rows", "constant"])
        self.scaler = QtWidgets.QComboBox()
        self.scaler.addItems(["standard", "minmax", "none"])
        self.fill_value = QtWidgets.QDoubleSpinBox()
        self.fill_value.setRange(-1_000_000_000, 1_000_000_000)
        self.fill_value.setDecimals(6)
        self.fill_value.setValue(0.0)
        self.test_size = QtWidgets.QDoubleSpinBox()
        self.test_size.setDecimals(2)
        self.test_size.setSingleStep(0.05)
        self.test_size.setRange(0.05, 0.8)
        self.test_size.setValue(0.2)
        self.random_state = QtWidgets.QSpinBox()
        self.random_state.setRange(0, 999999)
        self.random_state.setValue(42)

        form.addRow("缺失值处理", self.missing_strategy)
        form.addRow("缩放方式", self.scaler)
        form.addRow("常量填充值", self.fill_value)
        form.addRow("测试集比例", self.test_size)
        form.addRow("随机种子", self.random_state)

        self.apply_button = QtWidgets.QPushButton("应用预处理方案")
        self.apply_button.clicked.connect(self._emit_preprocess_requested)
        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.apply_button)
        button_row.addStretch(1)

        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.summary, stretch=1)

    def _emit_preprocess_requested(self) -> None:
        self.preprocess_requested.emit(
            self.missing_strategy.currentText(),
            self.scaler.currentText(),
            self.fill_value.value(),
            self.test_size.value(),
            self.random_state.value(),
        )

    def set_summary(self, text: str) -> None:
        self.summary.setPlainText(text)

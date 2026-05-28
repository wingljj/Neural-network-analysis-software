"""预测导出页面。"""

from __future__ import annotations

from pathlib import Path

from nn_qt.qt_compat import Signal, QtWidgets


class PredictPage(QtWidgets.QWidget):
    """加载模型并对新 Excel 执行预测。"""

    predict_requested = Signal(str, str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.model_path = QtWidgets.QLineEdit()
        self.input_path = QtWidgets.QLineEdit()
        self.output_path = QtWidgets.QLineEdit()
        self._output_auto_filled = False
        for edit in (self.model_path, self.input_path, self.output_path):
            edit.setReadOnly(True)
        self.model_button = QtWidgets.QPushButton("浏览")
        self.input_button = QtWidgets.QPushButton("浏览")
        self.output_button = QtWidgets.QPushButton("保存到")
        self.model_button.clicked.connect(self.choose_model_file)
        self.input_button.clicked.connect(self.choose_input_file)
        self.output_button.clicked.connect(self.choose_output_file)
        form.addRow("模型文件", self._path_row(self.model_path, self.model_button))
        form.addRow("预测 Excel", self._path_row(self.input_path, self.input_button))
        form.addRow("输出 Excel", self._path_row(self.output_path, self.output_button))

        predict_button = QtWidgets.QPushButton("执行预测并导出")
        predict_button.clicked.connect(self._emit_predict_requested)
        self.result = QtWidgets.QTextEdit()
        self.result.setReadOnly(True)
        layout.addLayout(form)
        layout.addWidget(predict_button)
        layout.addWidget(self.result)

    def _emit_predict_requested(self) -> None:
        self.predict_requested.emit(
            self.model_path.text(),
            self.input_path.text(),
            self.output_path.text(),
        )

    def choose_model_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            "",
            "Model Files (*.joblib)",
        )
        if path:
            self.model_path.setText(path)

    def choose_input_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择预测 Excel",
            "",
            "Excel Files (*.xlsx *.xls)",
        )
        if path:
            self.input_path.setText(path)
            input_path = Path(path)
            auto_output = str(input_path.with_name(f"{input_path.stem}_predictions.xlsx"))
            if not self.output_path.text() or self._output_auto_filled:
                self.output_path.setText(auto_output)
                self._output_auto_filled = True

    def choose_output_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "选择预测结果保存路径",
            self.output_path.text() or "predictions.xlsx",
            "Excel Files (*.xlsx)",
        )
        if path:
            if not path.lower().endswith(".xlsx"):
                path = f"{path}.xlsx"
            self.output_path.setText(path)
            self._output_auto_filled = False

    def _path_row(
        self,
        edit: QtWidgets.QLineEdit,
        button: QtWidgets.QPushButton,
    ) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit, stretch=1)
        layout.addWidget(button)
        return widget

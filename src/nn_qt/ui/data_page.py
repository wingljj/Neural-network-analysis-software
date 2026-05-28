"""数据导入页面。"""

from __future__ import annotations

from nn_qt.qt_compat import Signal, QtWidgets


class DataPage(QtWidgets.QWidget):
    """Excel 导入和 N/M 列配置。"""

    import_requested = Signal(str, int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.feature_count = QtWidgets.QSpinBox()
        self.feature_count.setRange(1, 10000)
        self.feature_count.setValue(3)
        self.target_count = QtWidgets.QSpinBox()
        self.target_count.setRange(1, 10000)
        self.target_count.setValue(1)
        form.addRow("Excel 文件", self.path_edit)
        form.addRow("前 N 列输入", self.feature_count)
        form.addRow("后 M 列输出", self.target_count)

        button_row = QtWidgets.QHBoxLayout()
        browse = QtWidgets.QPushButton("导入 Excel")
        browse.clicked.connect(self._choose_file)
        button_row.addWidget(browse)
        button_row.addStretch(1)

        self.preview = QtWidgets.QTableWidget(0, 0)
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.preview)

    def _choose_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择 Excel 文件",
            "",
            "Excel Files (*.xlsx *.xls)",
        )
        if path:
            self.path_edit.setText(path)
            self.import_requested.emit(
                path,
                self.feature_count.value(),
                self.target_count.value(),
            )

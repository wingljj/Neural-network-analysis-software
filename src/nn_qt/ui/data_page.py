"""数据导入页面。"""

from __future__ import annotations

from nn_qt.qt_compat import QtCore, Signal, QtWidgets


ROLE_FEATURE = "输入变量"
ROLE_TARGET = "输出变量"
ROLE_IGNORE = "忽略"
ROLE_OPTIONS = [ROLE_FEATURE, ROLE_TARGET, ROLE_IGNORE]


class DataPage(QtWidgets.QWidget):
    """Excel 导入、原始数据预览和列角色配置。"""

    import_requested = Signal(str)
    columns_selected = Signal(list, list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.path_edit = QtWidgets.QLineEdit()
        form.addRow("Excel 文件", self.path_edit)

        button_row = QtWidgets.QHBoxLayout()
        browse = QtWidgets.QPushButton("导入 Excel")
        browse.clicked.connect(self._choose_file)
        button_row.addWidget(browse)
        button_row.addStretch(1)

        self.column_roles = QtWidgets.QTableWidget(0, 2)
        self.column_roles.setHorizontalHeaderLabels(["列名", "变量角色"])
        self.column_roles.verticalHeader().setVisible(False)
        self.column_roles.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.column_roles.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.column_roles.setAlternatingRowColors(True)
        role_header = self.column_roles.horizontalHeader()
        role_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        role_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.apply_columns_button = QtWidgets.QPushButton("应用变量设置")
        self.apply_columns_button.setEnabled(False)
        self.apply_columns_button.clicked.connect(self._emit_columns_selected)

        self.preview = QtWidgets.QTableWidget(0, 0)
        self.preview.setAlternatingRowColors(True)
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.column_roles)
        layout.addWidget(self.apply_columns_button)
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
            self.import_requested.emit(path)

    def set_columns(self, columns: list) -> None:
        """导入 Excel 后，根据真实列名生成变量角色选择表。"""

        self.column_roles.setRowCount(len(columns))
        for row, column in enumerate(columns):
            item = QtWidgets.QTableWidgetItem(str(column))
            item.setData(QtCore.Qt.UserRole, column)
            self.column_roles.setItem(row, 0, item)

            role_combo = QtWidgets.QComboBox()
            role_combo.addItems(ROLE_OPTIONS)
            default_role = ROLE_FEATURE if row < len(columns) - 1 else ROLE_TARGET
            role_combo.setCurrentText(default_role)
            self.column_roles.setCellWidget(row, 1, role_combo)

        self.apply_columns_button.setEnabled(bool(columns))
        self.column_roles.resizeRowsToContents()

    def selected_feature_target_columns(self) -> tuple[list, list]:
        """读取当前列角色配置，返回输入列和输出列。"""

        feature_columns = []
        target_columns = []
        for row in range(self.column_roles.rowCount()):
            item = self.column_roles.item(row, 0)
            if item is None:
                continue
            column = item.data(QtCore.Qt.UserRole)
            role_widget = self.column_roles.cellWidget(row, 1)
            role = role_widget.currentText() if role_widget is not None else ROLE_IGNORE
            if role == ROLE_FEATURE:
                feature_columns.append(column)
            elif role == ROLE_TARGET:
                target_columns.append(column)
        return feature_columns, target_columns

    def set_column_role(self, column_name: str, role: str) -> None:
        """按列名修改角色，供自动化测试和后续快捷操作复用。"""

        if role not in ROLE_OPTIONS:
            raise ValueError(f"未知变量角色: {role}")
        for row in range(self.column_roles.rowCount()):
            item = self.column_roles.item(row, 0)
            if item is not None and item.text() == str(column_name):
                role_widget = self.column_roles.cellWidget(row, 1)
                if role_widget is not None:
                    role_widget.setCurrentText(role)
                    return
        raise ValueError(f"未找到列: {column_name}")

    def _emit_columns_selected(self) -> None:
        feature_columns, target_columns = self.selected_feature_target_columns()
        self.columns_selected.emit(feature_columns, target_columns)

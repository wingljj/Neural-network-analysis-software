"""左侧功能导航。"""

from __future__ import annotations

from nn_qt.qt_compat import Signal, QtCore, QtWidgets
from nn_qt.ui.theme import configure_sidebar_font, refresh_sidebar_metrics


class SidebarWidget(QtWidgets.QListWidget):
    """侧边栏导航控件。"""

    page_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.addItems(["数据导入", "机器学习预处理", "统计分析", "模型训练", "预测导出"])
        self.setCurrentRow(0)
        self.currentRowChanged.connect(self.page_changed.emit)
        configure_sidebar_font(self)
        refresh_sidebar_metrics(self)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.FontChange:
            refresh_sidebar_metrics(self)

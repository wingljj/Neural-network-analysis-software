"""统计分析页面。"""

from __future__ import annotations

from nn_qt.qt_compat import Signal, QtWidgets
from nn_qt.ui.chart_widget import ChartWidget


class AnalysisPage(QtWidgets.QWidget):
    """PCA、ANOVA 和灵敏度分析入口。"""

    pca_requested = Signal()
    anova_requested = Signal()
    sensitivity_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()
        pca_button = QtWidgets.QPushButton("PCA 分析")
        anova_button = QtWidgets.QPushButton("ANOVA")
        sensitivity_button = QtWidgets.QPushButton("灵敏度分析")
        pca_button.clicked.connect(self.pca_requested.emit)
        anova_button.clicked.connect(self.anova_requested.emit)
        sensitivity_button.clicked.connect(self.sensitivity_requested.emit)
        toolbar.addWidget(pca_button)
        toolbar.addWidget(anova_button)
        toolbar.addWidget(sensitivity_button)
        toolbar.addStretch(1)

        self.chart = ChartWidget()
        self.result_table = QtWidgets.QTableWidget(0, 0)
        layout.addLayout(toolbar)
        layout.addWidget(self.chart, stretch=2)
        layout.addWidget(self.result_table, stretch=1)

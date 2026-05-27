"""Matplotlib 画布封装。"""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    """统一管理主界面中的图表绘制。"""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(7, 5), tight_layout=True)
        super().__init__(self.figure)
        self.setMinimumHeight(360)

    def clear(self) -> None:
        self.figure.clear()
        self.draw_idle()

    def plot_pca(self, components: np.ndarray, explained_variance_ratio: np.ndarray) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.scatter(components[:, 0], components[:, 1], alpha=0.75, edgecolor="white")
        axis.set_title("PCA 主成分散点图")
        axis.set_xlabel(f"PC1 ({explained_variance_ratio[0] * 100:.2f}%)")
        axis.set_ylabel(f"PC2 ({explained_variance_ratio[1] * 100:.2f}%)")
        axis.grid(alpha=0.25)
        self.draw_idle()

    def plot_importance(self, table: pd.DataFrame) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        top = table.head(20).sort_values("importance_mean", ascending=True)
        axis.barh(top["feature"], top["importance_mean"], xerr=top["importance_std"], color="#2f7dd1")
        axis.set_title("特征灵敏度 / 置换重要性")
        axis.set_xlabel("重要性均值")
        axis.grid(axis="x", alpha=0.25)
        self.draw_idle()

    def plot_prediction(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        true = np.asarray(y_true)
        pred = np.asarray(y_pred)
        if true.ndim > 1:
            true = true[:, 0]
        if pred.ndim > 1:
            pred = pred[:, 0]
        axis.plot(true, label="真实值", linewidth=1.8)
        axis.plot(pred, label="预测值", linewidth=1.8)
        axis.set_title("真实值 vs 预测值")
        axis.set_xlabel("测试样本序号")
        axis.set_ylabel("目标值")
        axis.grid(alpha=0.25)
        axis.legend()
        self.draw_idle()

    def plot_loss(self, loss_curve: list[float]) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.plot(loss_curve, color="#d55e00", linewidth=1.8)
        axis.set_title("Loss 下降曲线")
        axis.set_xlabel("迭代轮次")
        axis.set_ylabel("Loss")
        axis.grid(alpha=0.25)
        self.draw_idle()

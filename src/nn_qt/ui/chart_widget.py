"""matplotlib 图表嵌入控件。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from nn_qt.qt_compat import QtWidgets


class ChartWidget(QtWidgets.QWidget):
    """统一封装绘图画布。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        configure_matplotlib_style()
        layout = QtWidgets.QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 3), tight_layout=True)
        self.figure.set_facecolor("#ffffff")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.plot_placeholder("等待分析结果")

    def plot_placeholder(self, text: str) -> None:
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        self._style_axes(axes, grid=False)
        axes.text(0.5, 0.5, text, ha="center", va="center")
        axes.set_axis_off()
        self.canvas.draw_idle()

    def plot_loss(self, values: list[float], total_epochs: int | None = None) -> None:
        if not values:
            self.plot_placeholder("暂无 Loss 数据")
            return
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        self._style_axes(axes)
        epochs = list(range(1, len(values) + 1))
        axes.plot(epochs, values, color="#2f6fed", linewidth=1.8)
        axes.scatter([epochs[-1]], [values[-1]], s=28, color="#2f6fed", zorder=3)
        x_max = max(total_epochs or len(values), len(values), 2)
        axes.set_xlim(1, x_max)
        axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        axes.set_title("Training Loss")
        axes.set_xlabel("Epoch")
        axes.set_ylabel("Loss")
        self.canvas.draw_idle()

    def plot_pca(self, result) -> None:
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        self._style_axes(axes)
        components = result.components
        x = components.iloc[:, 0]
        if components.shape[1] > 1:
            y = components.iloc[:, 1]
            y_label = self._pc_label("PC2", result.explained_variance_ratio, 1)
        else:
            y = np.zeros(len(x))
            y_label = "PC2"
        axes.scatter(
            x,
            y,
            s=42,
            color="#2f6fed",
            edgecolors="#ffffff",
            linewidths=0.7,
            alpha=0.86,
        )
        axes.axhline(0, color="#b8c2cc", linewidth=0.8, zorder=0)
        axes.axvline(0, color="#b8c2cc", linewidth=0.8, zorder=0)
        axes.set_xlabel(self._pc_label("PC1", result.explained_variance_ratio, 0))
        axes.set_ylabel(y_label)
        axes.set_title("PCA 主成分散点图")
        self.canvas.draw_idle()

    def plot_anova(self, result) -> None:
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        self._style_axes(axes)
        p_values = result.p_values.replace(0, np.nextafter(0, 1))
        scores = (-np.log10(p_values)).mean(axis=0).sort_values()
        threshold = -np.log10(0.05)
        colors = ["#91b7f2" if value >= threshold else "#c8d3df" for value in scores]
        axes.barh(scores.index.astype(str), scores.values, color=colors)
        axes.axvline(threshold, color="#d65f5f", linewidth=1.0, linestyle="--")
        axes.set_xlabel("-log10(p)")
        axes.set_ylabel("Feature")
        axes.set_title("ANOVA 显著性")
        self.canvas.draw_idle()

    def plot_sensitivity(self, result) -> None:
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        self._style_axes(axes)
        data = result.importance.sort_values("importance", ascending=True).tail(20)
        axes.barh(data["feature"].astype(str), data["importance"], color="#4b8bbe")
        axes.set_xlabel("Importance")
        axes.set_ylabel("Feature")
        axes.set_title("特征重要性")
        self.canvas.draw_idle()

    def _style_axes(self, axes, grid: bool = True) -> None:
        axes.set_facecolor("#ffffff")
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)
        axes.spines["left"].set_color("#6b7785")
        axes.spines["bottom"].set_color("#6b7785")
        axes.tick_params(direction="out", colors="#334155", labelsize=9)
        axes.title.set_fontsize(11)
        axes.xaxis.label.set_fontsize(10)
        axes.yaxis.label.set_fontsize(10)
        if grid:
            axes.grid(axis="y", color="#e3e8ef", linewidth=0.8)
            axes.set_axisbelow(True)

    def _pc_label(self, name: str, ratios: list[float], index: int) -> str:
        if index < len(ratios):
            return f"{name} ({ratios[index] * 100:.1f}%)"
        return name


def configure_matplotlib_style() -> None:
    """配置中文字体和论文风格 matplotlib 参数。"""

    font_names: list[str] = []
    for path in (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ):
        if path.exists():
            font_manager.fontManager.addfont(str(path))
            font_names.append(font_manager.FontProperties(fname=str(path)).get_name())

    font_names.extend(
        [
            "Microsoft YaHei",
            "SimHei",
            "Noto Sans CJK SC",
            "Source Han Sans SC",
            "Arial Unicode MS",
            "DejaVu Sans",
        ]
    )
    rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": font_names,
            "axes.unicode_minus": False,
            "figure.facecolor": "#ffffff",
            "axes.facecolor": "#ffffff",
            "savefig.facecolor": "#ffffff",
            "axes.linewidth": 0.8,
            "xtick.direction": "out",
            "ytick.direction": "out",
        }
    )

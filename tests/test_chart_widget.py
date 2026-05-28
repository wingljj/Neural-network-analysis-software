import os
import warnings

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_compat = pytest.importorskip("nn_qt.qt_compat")
QtWidgets = qt_compat.QtWidgets

from nn_qt.models.result_models import AnovaResult, PcaResult, SensitivityResult
from nn_qt.ui.chart_widget import ChartWidget


def _app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _draw_without_missing_glyph_warning(chart: ChartWidget):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        chart.canvas.draw()
    glyph_warnings = [item for item in caught if "Glyph" in str(item.message)]
    assert glyph_warnings == []


def test_chart_widget_renders_chinese_and_negative_values_without_glyph_warning():
    app = _app()
    assert app is not None
    chart = ChartWidget()

    chart.plot_placeholder("中文标题 - 负号 -1.23")

    _draw_without_missing_glyph_warning(chart)


def test_chart_widget_has_publication_style_facecolor_and_axes():
    app = _app()
    assert app is not None
    chart = ChartWidget()

    chart.plot_loss([1.0, 0.5, 0.25])

    assert chart.figure.get_facecolor() == (1.0, 1.0, 1.0, 1.0)
    axes = chart.figure.axes[0]
    assert not axes.spines["top"].get_visible()
    assert not axes.spines["right"].get_visible()


def test_loss_plot_x_axis_adapts_to_configured_epochs():
    app = _app()
    assert app is not None
    chart = ChartWidget()

    chart.plot_loss([1.0 / value for value in range(1, 101)], total_epochs=300)

    axes = chart.figure.axes[0]
    assert axes.get_xlim()[1] >= 300


def test_chart_widget_can_plot_analysis_results_with_chinese_labels():
    app = _app()
    assert app is not None
    chart = ChartWidget()
    pca = PcaResult(
        components=pd.DataFrame({"PC1": [-1.0, 1.0], "PC2": [0.5, -0.5]}),
        explained_variance_ratio=[0.7, 0.2],
    )
    anova = AnovaResult(
        f_values=pd.DataFrame([[10.0, 3.0]], index=["目标"], columns=["温度", "压力"]),
        p_values=pd.DataFrame([[0.001, 0.03]], index=["目标"], columns=["温度", "压力"]),
    )
    sensitivity = SensitivityResult(
        importance=pd.DataFrame({"feature": ["温度", "压力"], "importance": [0.8, 0.2]})
    )

    chart.plot_pca(pca)
    _draw_without_missing_glyph_warning(chart)
    chart.plot_anova(anova)
    _draw_without_missing_glyph_warning(chart)
    chart.plot_sensitivity(sensitivity)
    _draw_without_missing_glyph_warning(chart)


def test_anova_plot_highlights_significant_features():
    app = _app()
    assert app is not None
    chart = ChartWidget()
    anova = AnovaResult(
        f_values=pd.DataFrame([[10.0, 3.0]], index=["目标"], columns=["显著", "不显著"]),
        p_values=pd.DataFrame([[0.001, 0.50]], index=["目标"], columns=["显著", "不显著"]),
    )

    chart.plot_anova(anova)

    axes = chart.figure.axes[0]
    labels = [tick.get_text() for tick in axes.get_yticklabels()]
    bars = axes.patches
    colors = {
        label: tuple(round(channel, 3) for channel in bar.get_facecolor()[:3])
        for label, bar in zip(labels, bars)
    }
    assert colors["显著"] != colors["不显著"]
    assert colors["显著"] == (0.569, 0.718, 0.949)

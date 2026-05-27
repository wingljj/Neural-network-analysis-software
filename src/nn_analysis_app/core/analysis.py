"""统计分析、降维分析与灵敏度分析。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.multioutput import MultiOutputRegressor


@dataclass
class PCAResult:
    """PCA 分析结果。"""

    components: np.ndarray
    explained_variance_ratio: np.ndarray
    labels: list[str]


@dataclass
class AnovaResult:
    """方差分析结果。"""

    table: pd.DataFrame


@dataclass
class SensitivityResult:
    """灵敏度分析结果。"""

    importance_table: pd.DataFrame


def run_pca(features: pd.DataFrame, scaled_features: np.ndarray) -> PCAResult:
    """计算前两个主成分及其方差解释率。"""
    if features.shape[0] < 2:
        raise ValueError("PCA 至少需要 2 行样本")
    if features.shape[1] < 2:
        raise ValueError("PCA 至少需要 2 个输入变量")

    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(scaled_features)
    return PCAResult(
        components=components,
        explained_variance_ratio=pca.explained_variance_ratio_,
        labels=["PC1", "PC2"],
    )


def run_anova(features: pd.DataFrame, targets: pd.DataFrame) -> AnovaResult:
    """对每个目标变量分别做单因素方差分析。

    这里使用 statsmodels 为每组「单个输入变量 -> 单个目标变量」拟合 OLS，
    再读取模型整体 F 检验的 F-value 和 p-value。这样不依赖公式字符串，
    能兼容中文列名、空格列名和特殊字符列名。
    """
    rows: list[dict[str, float | str]] = []

    for target_name in targets.columns:
        y = targets[target_name].to_numpy(dtype=float)
        for feature_name in features.columns:
            x = sm.add_constant(features[[feature_name]].to_numpy(dtype=float))
            model = sm.OLS(y, x, missing="drop").fit()
            rows.append(
                {
                    "target": str(target_name),
                    "feature": str(feature_name),
                    "f_value": float(model.fvalue),
                    "p_value": float(model.f_pvalue),
                }
            )

    table = pd.DataFrame(rows).sort_values(["target", "p_value"], ignore_index=True)
    return AnovaResult(table=table)


def run_sensitivity_analysis(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    random_state: int = 42,
    n_estimators: int = 100,
    n_repeats: int = 5,
) -> SensitivityResult:
    """使用随机森林和置换重要性估计输入变量影响程度。"""
    x = features.to_numpy(dtype=float)
    y = targets.to_numpy(dtype=float)
    if y.ndim == 2 and y.shape[1] == 1:
        y = y.ravel()

    # 小表格使用串行更快；大数据再启用多核并行，避免线程池启动开销拖慢 UI。
    n_jobs = -1 if x.shape[0] * x.shape[1] >= 5000 else 1
    base_model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=n_jobs,
    )
    model = base_model if np.ndim(y) == 1 else MultiOutputRegressor(base_model)
    model.fit(x, y)

    permutation = permutation_importance(
        model,
        x,
        y,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=n_jobs,
    )

    table = pd.DataFrame(
        {
            "feature": [str(name) for name in features.columns],
            "importance_mean": permutation.importances_mean,
            "importance_std": permutation.importances_std,
        }
    ).sort_values("importance_mean", ascending=False, ignore_index=True)
    return SensitivityResult(importance_table=table)

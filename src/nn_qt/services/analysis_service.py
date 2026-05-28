"""统计分析服务：PCA、ANOVA 和灵敏度分析。"""

from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import f_regression

from nn_qt.models.data_models import ProcessedBundle
from nn_qt.models.result_models import AnovaResult, PcaResult, SensitivityResult


class AnalysisService:
    """提供不依赖 Qt 的统计分析能力。"""

    def run_pca(self, bundle: ProcessedBundle, n_components: int = 2) -> PcaResult:
        max_components = min(n_components, bundle.X.shape[0], bundle.X.shape[1])
        if max_components <= 0:
            raise ValueError("PCA 至少需要一个样本和一个特征")

        pca = PCA(n_components=max_components, random_state=0)
        components = pca.fit_transform(bundle.X)
        columns = [f"PC{i + 1}" for i in range(max_components)]
        return PcaResult(
            components=pd.DataFrame(components, columns=columns),
            explained_variance_ratio=pca.explained_variance_ratio_.tolist(),
        )

    def run_anova(self, bundle: ProcessedBundle) -> AnovaResult:
        f_rows: dict[str, list[float]] = {}
        p_rows: dict[str, list[float]] = {}

        for target_name in bundle.target_names:
            f_values, p_values = f_regression(bundle.X, bundle.y[target_name])
            f_rows[target_name] = f_values.tolist()
            p_rows[target_name] = p_values.tolist()

        return AnovaResult(
            f_values=pd.DataFrame.from_dict(
                f_rows,
                orient="index",
                columns=bundle.feature_names,
            ),
            p_values=pd.DataFrame.from_dict(
                p_rows,
                orient="index",
                columns=bundle.feature_names,
            ),
        )

    def run_sensitivity(
        self,
        bundle: ProcessedBundle,
        random_state: int = 42,
    ) -> SensitivityResult:
        forest = RandomForestRegressor(
            n_estimators=80,
            random_state=random_state,
        )
        y = bundle.y
        forest.fit(bundle.X, y if y.shape[1] > 1 else y.iloc[:, 0])
        return SensitivityResult(
            importance=pd.DataFrame(
                {
                    "feature": bundle.feature_names,
                    "importance": forest.feature_importances_.tolist(),
                }
            ).sort_values("importance", ascending=False, ignore_index=True)
        )

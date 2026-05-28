"""模型包持久化服务。"""

from __future__ import annotations

from pathlib import Path

import joblib

from nn_qt.models.result_models import ModelPackage


class ModelStore:
    """使用 joblib 保存和加载完整推理包。"""

    def save(self, package: ModelPackage, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(package, output_path)

    def load(self, path: str | Path) -> ModelPackage:
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        package = joblib.load(model_path)
        if not isinstance(package, ModelPackage):
            raise ValueError("模型文件不是有效的 ModelPackage")
        return package

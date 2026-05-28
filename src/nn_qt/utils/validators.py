"""界面参数校验辅助函数。"""

from __future__ import annotations

from nn_qt.models.train_models import parse_hidden_layers


def validate_hidden_layers(text: str) -> tuple[int, ...]:
    """校验隐藏层输入并返回元组。"""

    return parse_hidden_layers(text)


def require_path(text: str, label: str) -> str:
    """确保路径文本不为空。"""

    value = text.strip()
    if not value:
        raise ValueError(f"{label}不能为空")
    return value

"""模型训练配置。"""

from __future__ import annotations

from dataclasses import dataclass


def parse_hidden_layers(text: str) -> tuple[int, ...]:
    """将界面输入的隐藏层字符串解析为 sklearn 需要的元组。"""

    values: list[int] = []
    for raw_part in text.split(","):
        part = raw_part.strip()
        if not part:
            continue
        value = int(part)
        if value <= 0:
            raise ValueError("hidden_layers 中的节点数必须为正整数")
        values.append(value)
    if not values:
        raise ValueError("hidden_layers 至少需要一个隐藏层节点数")
    return tuple(values)


@dataclass(frozen=True)
class TrainConfig:
    """神经网络训练参数。"""

    hidden_layers: tuple[int, ...]
    learning_rate: float
    epochs: int
    test_size: float = 0.2
    random_state: int = 42

    def __post_init__(self) -> None:
        if not self.hidden_layers or any(node <= 0 for node in self.hidden_layers):
            raise ValueError("hidden_layers 必须包含正整数")
        if self.learning_rate <= 0:
            raise ValueError("learning_rate 必须大于 0")
        if self.epochs <= 0:
            raise ValueError("epochs 必须为正整数")
        if not 0 < self.test_size < 1:
            raise ValueError("test_size 必须位于 0 到 1 之间")

"""Qt 后台任务线程。

耗时的数据分析和模型训练放入 QThread，避免主界面在计算时失去响应。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    """后台任务信号集合。"""

    started = pyqtSignal(str)
    log = pyqtSignal(str)
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)


class FunctionWorker(QRunnable):
    """把普通 Python 函数包装成 Qt 线程池任务。"""

    def __init__(self, title: str, function: Callable[..., Any], *args: Any, **kwargs: Any):
        super().__init__()
        self.title = title
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self) -> None:
        """在线程池中执行任务，并通过信号回传结果。"""
        self.signals.started.emit(self.title)
        try:
            result = self.function(*self.args, **self.kwargs)
        except Exception as exc:  # noqa: BLE001 - GUI 层需要把任何异常转成日志
            self.signals.failed.emit(f"{self.title} 失败：{exc}")
            return
        self.signals.finished.emit(result)


def default_output_path(source_path: str | Path, suffix: str, extension: str) -> Path:
    """根据输入文件生成默认导出路径。"""
    source = Path(source_path)
    return source.with_name(f"{source.stem}_{suffix}{extension}")

"""训练后台任务。"""

from __future__ import annotations

from nn_qt.models.data_models import ProcessedBundle
from nn_qt.models.train_models import TrainConfig
from nn_qt.qt_compat import Signal, Slot, QtCore
from nn_qt.services.training_service import TrainingService


class TrainWorker(QtCore.QObject):
    """可移动到 QThread 的训练 worker。"""

    finished = Signal(object)
    error_occurred = Signal(str)
    log_emitted = Signal(str)

    def __init__(self, bundle: ProcessedBundle, config: TrainConfig, parent=None) -> None:
        super().__init__(parent)
        self.bundle = bundle
        self.config = config
        self.service = TrainingService()

    @Slot()
    def run(self) -> None:
        try:
            self.log_emitted.emit("开始训练神经网络模型")
            self.finished.emit(self.service.train(self.bundle, self.config))
            self.log_emitted.emit("模型训练完成")
        except Exception as exc:
            self.error_occurred.emit(str(exc))

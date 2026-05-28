"""预测后台任务。"""

from __future__ import annotations

from nn_qt.qt_compat import Signal, Slot, QtCore
from nn_qt.services.prediction_service import PredictionService


class PredictWorker(QtCore.QObject):
    """可移动到 QThread 的预测 worker。"""

    finished = Signal(object)
    error_occurred = Signal(str)
    log_emitted = Signal(str)

    def __init__(
        self,
        model_path: str,
        input_path: str,
        output_path: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.model_path = model_path
        self.input_path = input_path
        self.output_path = output_path
        self.service = PredictionService()

    @Slot()
    def run(self) -> None:
        try:
            self.log_emitted.emit("开始执行预测")
            result = self.service.predict_excel(
                self.model_path,
                self.input_path,
                self.output_path,
            )
            self.finished.emit(result)
            self.log_emitted.emit("预测结果已导出")
        except Exception as exc:
            self.error_occurred.emit(str(exc))

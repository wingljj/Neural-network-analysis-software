"""应用主窗口。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from nn_qt.config import APP_NAME
from nn_qt.models.data_models import ExcelLoadConfig, PreprocessConfig
from nn_qt.models.train_models import TrainConfig, parse_hidden_layers
from nn_qt.qt_compat import QtCore, QtWidgets
from nn_qt.services.analysis_service import AnalysisService
from nn_qt.services.data_service import DataService
from nn_qt.services.model_store import ModelStore
from nn_qt.ui.analysis_page import AnalysisPage
from nn_qt.ui.data_page import DataPage
from nn_qt.ui.log_panel import LogPanel
from nn_qt.ui.ml_preprocess_page import MlPreprocessPage
from nn_qt.ui.predict_page import PredictPage
from nn_qt.ui.sidebar import SidebarWidget
from nn_qt.ui.theme import (
    configure_application_font,
    configure_sidebar_font,
    refresh_sidebar_metrics,
    white_theme_stylesheet,
)
from nn_qt.ui.train_page import TrainPage
from nn_qt.workers.predict_worker import PredictWorker
from nn_qt.workers.train_worker import TrainWorker


class MainWindow(QtWidgets.QMainWindow):
    """包含侧边栏、页面栈和日志区的主窗口。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.sidebar = SidebarWidget()
        self.stack = QtWidgets.QStackedWidget()
        self.log_panel = LogPanel()

        self.data_page = DataPage()
        self.ml_preprocess_page = MlPreprocessPage()
        self.analysis_page = AnalysisPage()
        self.train_page = TrainPage()
        self.predict_page = PredictPage()
        self.data_service = DataService()
        self.analysis_service = AnalysisService()
        self.model_store = ModelStore()
        self.dataset_bundle = None
        self.processed_bundle = None
        self.train_result = None
        self._last_data_path: str | None = None
        self._last_model_dir: Path | None = None
        self._ml_random_state = 42
        self._running_threads: list[tuple[QtCore.QThread, QtCore.QObject]] = []
        for page in (
            self.data_page,
            self.ml_preprocess_page,
            self.analysis_page,
            self.train_page,
            self.predict_page,
        ):
            self.stack.addWidget(page)

        self.sidebar.page_changed.connect(self.stack.setCurrentIndex)
        self.data_page.import_requested.connect(self._handle_import_requested)
        self.ml_preprocess_page.preprocess_requested.connect(
            self._handle_ml_preprocess_requested
        )
        self.analysis_page.pca_requested.connect(self._handle_pca_requested)
        self.analysis_page.anova_requested.connect(self._handle_anova_requested)
        self.analysis_page.sensitivity_requested.connect(self._handle_sensitivity_requested)
        self.train_page.train_requested.connect(self._handle_train_requested)
        self.train_page.save_model_requested.connect(self._handle_save_model_requested)
        self.predict_page.predict_requested.connect(self._handle_predict_requested)
        content = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        content.addWidget(self.sidebar)
        content.addWidget(self.stack)
        content.setStretchFactor(1, 1)

        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_splitter.addWidget(content)
        main_splitter.addWidget(self.log_panel)
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        self.setCentralWidget(main_splitter)
        self.statusBar().showMessage("就绪")
        self._apply_style()

    def _apply_style(self) -> None:
        app = QtWidgets.QApplication.instance()
        configure_application_font(app)
        if app is not None:
            self.setFont(app.font())
        configure_sidebar_font(self.sidebar)
        refresh_sidebar_metrics(self.sidebar)
        self.setStyleSheet(white_theme_stylesheet())

    def _handle_import_requested(
        self,
        path: str,
        feature_count: int,
        target_count: int,
    ) -> None:
        try:
            df = self.data_service.load_excel(
                ExcelLoadConfig(
                    path=path,
                    feature_count=feature_count,
                    target_count=target_count,
                )
            )
            self.dataset_bundle = self.data_service.split_features_targets(
                df,
                feature_count=feature_count,
                target_count=target_count,
            )
            preprocess_config = self._current_ml_preprocess_config()
            self.processed_bundle = self.data_service.preprocess(
                self.dataset_bundle,
                preprocess_config,
            )
            self._populate_table(self.data_page.preview, df)
            self.ml_preprocess_page.set_summary(
                f"已按机器学习预处理页设置完成预处理\n"
                f"样本数：{len(self.processed_bundle.X)}\n"
                f"输入变量：{len(self.processed_bundle.feature_names)}\n"
                f"输出变量：{len(self.processed_bundle.target_names)}"
            )
            self._last_data_path = path
            self.log_panel.append_log(
                f"数据导入完成：{len(df)} 行，{len(df.columns)} 列"
            )
            self.statusBar().showMessage("数据导入完成")
        except Exception as exc:
            self._show_error(str(exc))

    def _current_ml_preprocess_config(self) -> PreprocessConfig:
        return PreprocessConfig(
            missing_strategy=self.ml_preprocess_page.missing_strategy.currentText(),
            scaler=self.ml_preprocess_page.scaler.currentText(),
            fill_value=self.ml_preprocess_page.fill_value.value(),
        )

    def _handle_ml_preprocess_requested(
        self,
        missing_strategy: str,
        scaler: str,
        fill_value: float,
        test_size: float,
        random_state: int,
    ) -> None:
        if self.dataset_bundle is None:
            self._show_error("请先导入 Excel 数据")
            return
        try:
            config = PreprocessConfig(
                missing_strategy=missing_strategy,
                scaler=scaler,
                fill_value=fill_value,
            )
            self.processed_bundle = self.data_service.preprocess(
                self.dataset_bundle,
                config,
            )
            self.train_page.test_size.setValue(test_size)
            self._ml_random_state = random_state
            self.ml_preprocess_page.set_summary(
                f"机器学习预处理已应用\n"
                f"缺失值处理：{missing_strategy}\n"
                f"缩放方式：{scaler}\n"
                f"测试集比例：{test_size:.2f}\n"
                f"随机种子：{random_state}\n"
                f"样本数：{len(self.processed_bundle.X)}"
            )
            self.log_panel.append_log("机器学习预处理已应用")
            self.statusBar().showMessage("机器学习预处理已应用")
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_pca_requested(self) -> None:
        if not self._require_processed_bundle():
            return
        try:
            result = self.analysis_service.run_pca(self.processed_bundle, n_components=2)
            self._populate_table(self.analysis_page.result_table, result.components)
            self.analysis_page.chart.plot_pca(result)
            self.log_panel.append_log("PCA 分析完成")
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_anova_requested(self) -> None:
        if not self._require_processed_bundle():
            return
        try:
            result = self.analysis_service.run_anova(self.processed_bundle)
            table = result.f_values.copy()
            table.columns = [f"F_{column}" for column in table.columns]
            self._populate_table(self.analysis_page.result_table, table)
            self.analysis_page.chart.plot_anova(result)
            self.log_panel.append_log("ANOVA 分析完成")
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_sensitivity_requested(self) -> None:
        if not self._require_processed_bundle():
            return
        try:
            result = self.analysis_service.run_sensitivity(self.processed_bundle)
            self._populate_table(self.analysis_page.result_table, result.importance)
            self.analysis_page.chart.plot_sensitivity(result)
            self.log_panel.append_log("灵敏度分析完成")
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_train_requested(
        self,
        hidden_layers_text: str,
        learning_rate: float,
        epochs: int,
        test_size: float,
    ) -> None:
        if not self._require_processed_bundle():
            return
        try:
            config = TrainConfig(
                hidden_layers=parse_hidden_layers(hidden_layers_text),
                learning_rate=learning_rate,
                epochs=epochs,
                test_size=test_size,
                random_state=self._ml_random_state,
            )
            worker = TrainWorker(self.processed_bundle, config)
            self._start_worker_thread(worker, self._handle_training_finished)
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_save_model_requested(self) -> None:
        if self.train_result is None:
            self._show_error("请先完成模型训练")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存模型",
            self._default_model_save_path(),
            "Model Files (*.joblib)",
        )
        if not path:
            return
        if not path.lower().endswith(".joblib"):
            path = f"{path}.joblib"
        try:
            self.model_store.save(self.train_result.model_package, path)
            self._last_model_dir = Path(path).parent
            self.predict_page.model_path.setText(path)
            self.log_panel.append_log(f"模型已保存：{path}")
        except Exception as exc:
            self._show_error(str(exc))

    def _default_model_save_path(self) -> str:
        """为模型保存对话框生成用户容易找到的默认路径。"""

        filename = f"model_{datetime.now():%Y%m%d_%H%M}.joblib"
        return str(self._default_model_dir() / filename)

    def _default_model_dir(self) -> Path:
        candidates = [
            self._last_data_path,
            self.predict_page.output_path.text(),
            str(self._last_model_dir) if self._last_model_dir else "",
        ]
        for raw_path in candidates:
            directory = self._existing_parent_dir(raw_path)
            if directory is not None:
                return directory

        documents_dir = Path.home() / "Documents"
        if documents_dir.exists():
            return documents_dir
        return Path.home()

    def _existing_parent_dir(self, raw_path: str) -> Path | None:
        if not raw_path:
            return None
        path = Path(raw_path).expanduser()
        directory = path if path.is_dir() else path.parent
        if directory.exists():
            return directory
        return None

    def _handle_predict_requested(
        self,
        model_path: str,
        input_path: str,
        output_path: str,
    ) -> None:
        if not model_path or not input_path or not output_path:
            self._show_error("模型文件、预测 Excel 和输出路径不能为空")
            return
        worker = PredictWorker(model_path, input_path, output_path)
        self._start_worker_thread(worker, self._handle_prediction_finished)

    def _handle_training_finished(self, result) -> None:
        self.train_result = result
        self.train_page.metrics.setPlainText(
            "\n".join(
                [
                    f"Train MSE: {result.train_mse:.6f}",
                    f"Train R2: {result.train_r2:.6f}",
                    f"Test MSE: {result.test_mse:.6f}",
                    f"Test R2: {result.test_r2:.6f}",
                ]
            )
        )
        self.train_page.chart.plot_loss(
            result.loss_curve,
            total_epochs=result.model_package.train_config.epochs,
        )
        self.train_page.set_save_enabled(True)
        self.log_panel.append_log("模型训练完成")

    def _handle_prediction_finished(self, result) -> None:
        self.predict_page.result.setPlainText(
            f"预测完成，输出文件：{result.output_path}\n"
            f"预测行数：{len(result.predictions)}"
        )
        self.log_panel.append_log("预测导出完成")

    def _start_worker_thread(self, worker: QtCore.QObject, finished_slot) -> None:
        thread = QtCore.QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(finished_slot)
        worker.finished.connect(thread.quit)
        worker.error_occurred.connect(self._show_error)
        worker.error_occurred.connect(thread.quit)
        worker.log_emitted.connect(self.log_panel.append_log)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread, worker))
        self._running_threads.append((thread, worker))
        thread.start()

    def _forget_thread(self, thread: QtCore.QThread, worker: QtCore.QObject) -> None:
        self._running_threads = [
            pair for pair in self._running_threads if pair != (thread, worker)
        ]
        thread.deleteLater()

    def _require_processed_bundle(self) -> bool:
        if self.processed_bundle is None:
            self._show_error("请先导入并预处理数据")
            return False
        return True

    def _populate_table(self, table: QtWidgets.QTableWidget, df) -> None:
        table.setRowCount(len(df.index))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels([str(column) for column in df.columns])
        for row_index, (_, row) in enumerate(df.iterrows()):
            for column_index, value in enumerate(row):
                table.setItem(
                    row_index,
                    column_index,
                    QtWidgets.QTableWidgetItem(str(value)),
                )
        table.resizeColumnsToContents()

    def _show_error(self, message: str) -> None:
        self.log_panel.append_log(f"错误：{message}")
        self.statusBar().showMessage(message)

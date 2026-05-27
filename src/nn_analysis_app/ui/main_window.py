"""主窗口界面。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nn_analysis_app.core.analysis import (
    AnovaResult,
    PCAResult,
    SensitivityResult,
    run_anova,
    run_pca,
    run_sensitivity_analysis,
)
from nn_analysis_app.core.config import DataConfig, ModelBundle, TrainingConfig
from nn_analysis_app.core.data_io import (
    PreparedDataset,
    export_predictions,
    prepare_dataset,
    prepare_prediction_features,
    read_excel,
)
from nn_analysis_app.core.modeling import (
    TrainingResult,
    load_model,
    parse_hidden_layers,
    predict,
    save_model,
    train_mlp,
)
from nn_analysis_app.ui.plot_canvas import PlotCanvas
from nn_analysis_app.ui.workers import FunctionWorker, default_output_path


class MainWindow(QMainWindow):
    """数据分析与神经网络预测主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("数据分析与神经网络预测")
        self.resize(1280, 820)

        self.thread_pool = QThreadPool.globalInstance()
        self.dataframe: pd.DataFrame | None = None
        self.dataset: PreparedDataset | None = None
        self.excel_path: Path | None = None
        self.model_bundle: ModelBundle | None = None
        self.last_training_result: TrainingResult | None = None

        self._build_actions()
        self._build_ui()
        self._apply_style()

    def _build_actions(self) -> None:
        """创建菜单动作。"""
        import_action = QAction("导入 Excel", self)
        import_action.triggered.connect(self.import_excel)
        save_model_action = QAction("保存模型", self)
        save_model_action.triggered.connect(self.save_current_model)
        load_model_action = QAction("加载模型", self)
        load_model_action.triggered.connect(self.load_existing_model)

        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction(import_action)
        file_menu.addAction(save_model_action)
        file_menu.addAction(load_model_action)

    def _build_ui(self) -> None:
        """搭建主布局：左侧导航与参数区，右侧结果显示区。"""
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        main_area = self._build_main_area()
        root_layout.addWidget(sidebar)
        root_layout.addWidget(main_area, stretch=1)
        self.setCentralWidget(root)

    def _build_sidebar(self) -> QWidget:
        """创建左侧控制面板。"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(330)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("神经网络分析软件")
        title.setObjectName("appTitle")
        subtitle = QLabel("Excel 数据分析、统计检验、MLP 训练与离线预测")
        subtitle.setObjectName("appSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        data_group = QGroupBox("数据导入与预处理")
        data_form = QFormLayout(data_group)
        data_form.setLabelAlignment(Qt.AlignLeft)

        self.import_button = QPushButton("导入 Excel")
        self.import_button.clicked.connect(self.import_excel)
        self.current_file_label = QLabel("未选择文件")
        self.current_file_label.setWordWrap(True)
        self.feature_spin = QSpinBox()
        self.feature_spin.setRange(1, 1000)
        self.feature_spin.setValue(3)
        self.target_spin = QSpinBox()
        self.target_spin.setRange(1, 1000)
        self.target_spin.setValue(1)
        self.missing_combo = QComboBox()
        self.missing_combo.addItems(["均值填充", "删除缺失行"])
        self.scaler_combo = QComboBox()
        self.scaler_combo.addItems(["StandardScaler", "MinMaxScaler", "不缩放"])
        self.prepare_button = QPushButton("生成数据集")
        self.prepare_button.clicked.connect(self.prepare_current_dataset)

        data_form.addRow(self.import_button)
        data_form.addRow("当前文件", self.current_file_label)
        data_form.addRow("前 N 列输入", self.feature_spin)
        data_form.addRow("后 M 列输出", self.target_spin)
        data_form.addRow("缺失值处理", self.missing_combo)
        data_form.addRow("缩放方式", self.scaler_combo)
        data_form.addRow(self.prepare_button)
        layout.addWidget(data_group)

        train_group = QGroupBox("MLP 训练参数")
        train_form = QFormLayout(train_group)
        self.task_group = QButtonGroup(self)
        self.regression_radio = QRadioButton("回归")
        self.classification_radio = QRadioButton("分类")
        self.regression_radio.setChecked(True)
        self.task_group.addButton(self.regression_radio)
        self.task_group.addButton(self.classification_radio)
        task_row = QHBoxLayout()
        task_row.addWidget(self.regression_radio)
        task_row.addWidget(self.classification_radio)
        self.hidden_layers_edit = QLineEdit("64,32")
        self.learning_rate_edit = QLineEdit("0.001")
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(10, 20000)
        self.epochs_spin.setValue(300)
        self.test_size_combo = QComboBox()
        self.test_size_combo.addItems(["0.2", "0.25", "0.3"])
        self.train_button = QPushButton("训练模型")
        self.train_button.clicked.connect(self.train_model_async)
        self.save_model_button = QPushButton("保存模型")
        self.save_model_button.clicked.connect(self.save_current_model)

        train_form.addRow("任务类型", task_row)
        train_form.addRow("隐藏层", self.hidden_layers_edit)
        train_form.addRow("学习率", self.learning_rate_edit)
        train_form.addRow("Epochs", self.epochs_spin)
        train_form.addRow("测试集比例", self.test_size_combo)
        train_form.addRow(self.train_button)
        train_form.addRow(self.save_model_button)
        layout.addWidget(train_group)

        predict_group = QGroupBox("离线预测")
        predict_layout = QVBoxLayout(predict_group)
        self.load_model_button = QPushButton("加载模型")
        self.load_model_button.clicked.connect(self.load_existing_model)
        self.predict_button = QPushButton("导入新 Excel 并预测")
        self.predict_button.clicked.connect(self.predict_from_excel)
        predict_layout.addWidget(self.load_model_button)
        predict_layout.addWidget(self.predict_button)
        layout.addWidget(predict_group)

        layout.addStretch(1)
        return sidebar

    def _build_main_area(self) -> QWidget:
        """创建右侧结果区。"""
        main = QWidget()
        layout = QVBoxLayout(main)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        button_row = QHBoxLayout()
        self.pca_button = QPushButton("PCA 分析")
        self.pca_button.clicked.connect(self.run_pca_async)
        self.anova_button = QPushButton("ANOVA 分析")
        self.anova_button.clicked.connect(self.run_anova_async)
        self.sensitivity_button = QPushButton("灵敏度分析")
        self.sensitivity_button.clicked.connect(self.run_sensitivity_async)
        self.loss_button = QPushButton("显示 Loss 曲线")
        self.loss_button.clicked.connect(self.show_loss_curve)
        button_row.addWidget(self.pca_button)
        button_row.addWidget(self.anova_button)
        button_row.addWidget(self.sensitivity_button)
        button_row.addWidget(self.loss_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        splitter = QSplitter(Qt.Vertical)
        self.tabs = QTabWidget()
        self.preview_table = QTableWidget()
        self.result_table = QTableWidget()
        self.plot_canvas = PlotCanvas()
        self.tabs.addTab(self.preview_table, "数据预览")
        self.tabs.addTab(self.result_table, "统计结果")
        self.tabs.addTab(self.plot_canvas, "图表")

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(150)
        self.log_box.setObjectName("logBox")
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.log_box)
        splitter.setSizes([620, 180])
        layout.addWidget(splitter, stretch=1)
        return main

    def _apply_style(self) -> None:
        """设置简洁现代的桌面端样式。"""
        self.setFont(QFont("Microsoft YaHei UI", 10))
        QApplication.instance().setStyleSheet(
            """
            QMainWindow { background: #f4f6f8; }
            #sidebar { background: #18202a; color: #f7f9fb; }
            #appTitle { color: #ffffff; font-size: 22px; font-weight: 700; }
            #appSubtitle { color: #b7c1cc; line-height: 1.4; }
            QGroupBox {
                border: 1px solid #d8dee6;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                font-weight: 600;
            }
            #sidebar QGroupBox {
                border: 1px solid #384554;
                color: #f7f9fb;
            }
            QLabel { color: #293241; }
            #sidebar QLabel { color: #e5edf5; }
            QPushButton {
                background: #2f7dd1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background: #236bb5; }
            QPushButton:disabled { background: #aab4bf; }
            QLineEdit, QSpinBox, QComboBox, QTextEdit, QTableWidget {
                background: white;
                border: 1px solid #cfd7df;
                border-radius: 6px;
                padding: 5px;
            }
            #logBox {
                background: #101820;
                color: #c8f7c5;
                font-family: Consolas, Menlo, monospace;
            }
            QTabWidget::pane { border: 1px solid #d8dee6; border-radius: 8px; }
            """
        )

    def log(self, message: str) -> None:
        """向运行日志写入一行状态。"""
        self.log_box.append(message)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def import_excel(self) -> None:
        """导入训练 Excel 文件。"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Excel 文件",
            "",
            "Excel 文件 (*.xlsx *.xls)",
        )
        if not path:
            return

        try:
            self.dataframe = read_excel(path)
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return

        self.excel_path = Path(path)
        self.dataset = None
        self.current_file_label.setText(self.excel_path.name)
        self.feature_spin.setMaximum(max(1, self.dataframe.shape[1]))
        self.target_spin.setMaximum(max(1, self.dataframe.shape[1]))
        self.populate_table(self.preview_table, self.dataframe.head(100))
        self.tabs.setCurrentWidget(self.preview_table)
        self.log(f"已导入 Excel：{self.excel_path}，形状={self.dataframe.shape}")

    def prepare_current_dataset(self) -> None:
        """根据当前 UI 配置生成 PreparedDataset。"""
        if self.dataframe is None:
            self.show_error("请先导入 Excel 文件")
            return

        try:
            config = self.collect_data_config()
            self.dataset = prepare_dataset(self.dataframe, config)
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return

        self.log(
            f"数据集已生成：样本={self.dataset.features.shape[0]}，输入={len(self.dataset.feature_names)}，输出={len(self.dataset.target_names)}"
        )
        preview = pd.concat([self.dataset.features, self.dataset.targets], axis=1).head(100)
        self.populate_table(self.preview_table, preview)

    def collect_data_config(self) -> DataConfig:
        """收集数据配置。"""
        missing_map = {"均值填充": "mean", "删除缺失行": "drop"}
        scaler_map = {
            "StandardScaler": "standard",
            "MinMaxScaler": "minmax",
            "不缩放": "none",
        }
        return DataConfig(
            feature_count=self.feature_spin.value(),
            target_count=self.target_spin.value(),
            missing_strategy=missing_map[self.missing_combo.currentText()],
            scaler_type=scaler_map[self.scaler_combo.currentText()],
        )

    def collect_training_config(self) -> TrainingConfig:
        """收集训练配置。"""
        hidden_layers = parse_hidden_layers(self.hidden_layers_edit.text())
        task_type = "classification" if self.classification_radio.isChecked() else "regression"
        try:
            learning_rate = float(self.learning_rate_edit.text())
        except ValueError as exc:
            raise ValueError("学习率必须为数字") from exc
        if learning_rate <= 0:
            raise ValueError("学习率必须大于 0")

        return TrainingConfig(
            task_type=task_type,
            hidden_layers=hidden_layers,
            learning_rate=learning_rate,
            epochs=self.epochs_spin.value(),
            test_size=float(self.test_size_combo.currentText()),
        )

    def ensure_dataset(self) -> PreparedDataset:
        """确保当前已生成数据集，必要时自动生成。"""
        if self.dataset is None:
            self.prepare_current_dataset()
        if self.dataset is None:
            raise ValueError("数据集不可用")
        return self.dataset

    def run_pca_async(self) -> None:
        """异步执行 PCA。"""
        try:
            dataset = self.ensure_dataset()
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return
        self.start_worker("PCA 分析", run_pca, self.on_pca_finished, dataset.features, dataset.scaled_features)

    def run_anova_async(self) -> None:
        """异步执行 ANOVA。"""
        try:
            dataset = self.ensure_dataset()
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return
        self.start_worker("ANOVA 分析", run_anova, self.on_anova_finished, dataset.features, dataset.targets)

    def run_sensitivity_async(self) -> None:
        """异步执行灵敏度分析。"""
        try:
            dataset = self.ensure_dataset()
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return
        self.start_worker(
            "灵敏度分析",
            run_sensitivity_analysis,
            self.on_sensitivity_finished,
            dataset.features,
            dataset.targets,
        )

    def train_model_async(self) -> None:
        """异步训练 MLP 模型。"""
        try:
            dataset = self.ensure_dataset()
            config = self.collect_training_config()
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return

        def task() -> TrainingResult:
            return train_mlp(dataset, config)

        self.start_worker("MLP 模型训练", task, self.on_training_finished)

    def start_worker(
        self,
        title: str,
        function: Any,
        finished_callback: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """启动一个线程池任务。"""
        worker = FunctionWorker(title, function, *args, **kwargs)
        worker.signals.started.connect(lambda text: self.log(f"{text} 开始..."))
        worker.signals.failed.connect(self.on_worker_failed)
        worker.signals.finished.connect(finished_callback)
        self.thread_pool.start(worker)

    def on_worker_failed(self, message: str) -> None:
        """后台任务失败时提示用户。"""
        self.log(message)
        self.show_error(message)

    def on_pca_finished(self, result: PCAResult) -> None:
        """展示 PCA 结果。"""
        table = pd.DataFrame(
            {
                "主成分": result.labels,
                "方差解释率": result.explained_variance_ratio,
                "累计解释率": result.explained_variance_ratio.cumsum(),
            }
        )
        self.populate_table(self.result_table, table)
        self.plot_canvas.plot_pca(result.components, result.explained_variance_ratio)
        self.tabs.setCurrentWidget(self.plot_canvas)
        self.log("PCA 分析完成")

    def on_anova_finished(self, result: AnovaResult) -> None:
        """展示 ANOVA 表格。"""
        self.populate_table(self.result_table, result.table)
        self.tabs.setCurrentWidget(self.result_table)
        self.log("ANOVA 分析完成")

    def on_sensitivity_finished(self, result: SensitivityResult) -> None:
        """展示灵敏度分析结果。"""
        self.populate_table(self.result_table, result.importance_table)
        self.plot_canvas.plot_importance(result.importance_table)
        self.tabs.setCurrentWidget(self.plot_canvas)
        self.log("灵敏度分析完成")

    def on_training_finished(self, result: TrainingResult) -> None:
        """展示模型训练结果。"""
        self.last_training_result = result
        self.model_bundle = result.bundle
        metrics_df = pd.DataFrame(
            [{"指标": key, "值": value} for key, value in result.metrics.items()]
        )
        self.populate_table(self.result_table, metrics_df)
        self.plot_canvas.plot_prediction(result.y_test, result.y_pred)
        self.tabs.setCurrentWidget(self.plot_canvas)
        self.log("模型已训练并暂存在内存中，可点击“保存模型”导出 .joblib")

    def show_loss_curve(self) -> None:
        """显示最近一次训练的 Loss 曲线。"""
        if self.last_training_result is None:
            self.show_error("请先训练模型")
            return
        if not self.last_training_result.loss_curve:
            self.show_error("当前模型没有可用的 Loss 曲线")
            return
        self.plot_canvas.plot_loss(self.last_training_result.loss_curve)
        self.tabs.setCurrentWidget(self.plot_canvas)

    def save_current_model(self) -> None:
        """保存当前训练好的模型。"""
        if self.model_bundle is None:
            self.show_error("当前没有可保存的模型，请先训练或加载模型")
            return

        default_name = "mlp_model.joblib"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存模型",
            default_name,
            "Joblib 模型 (*.joblib)",
        )
        if not path:
            return
        try:
            saved_path = save_model(self.model_bundle, path)
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return
        self.log(f"模型已保存：{saved_path}")

    def load_existing_model(self) -> None:
        """加载已有模型。"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            "",
            "Joblib 模型 (*.joblib)",
        )
        if not path:
            return
        try:
            self.model_bundle = load_model(path)
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return
        self.log(
            f"模型已加载：{path}，输入列={len(self.model_bundle.feature_names)}，输出列={len(self.model_bundle.target_names)}"
        )

    def predict_from_excel(self) -> None:
        """导入新 Excel，使用当前模型预测并导出结果。"""
        if self.model_bundle is None:
            self.show_error("请先训练或加载模型")
            return

        input_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择待预测 Excel",
            "",
            "Excel 文件 (*.xlsx *.xls)",
        )
        if not input_path:
            return
        default_path = default_output_path(input_path, "predictions", ".xlsx")
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存预测结果",
            str(default_path),
            "Excel 文件 (*.xlsx)",
        )
        if not output_path:
            return

        try:
            source = read_excel(input_path)
            features = prepare_prediction_features(
                source,
                self.model_bundle.feature_names,
                self.model_bundle.scaler,
            )
            predictions = predict(self.model_bundle, features)
            exported_path = export_predictions(
                source,
                predictions,
                self.model_bundle.target_names,
                output_path,
            )
        except Exception as exc:  # noqa: BLE001
            self.show_error(str(exc))
            return
        self.log(f"预测完成，结果已导出：{exported_path}")
        QMessageBox.information(self, "预测完成", f"结果已导出：\n{exported_path}")

    def populate_table(self, table: QTableWidget, dataframe: pd.DataFrame) -> None:
        """把 pandas DataFrame 显示到 QTableWidget。"""
        table.clear()
        table.setRowCount(len(dataframe))
        table.setColumnCount(len(dataframe.columns))
        table.setHorizontalHeaderLabels([str(column) for column in dataframe.columns])
        for row_index, (_, row) in enumerate(dataframe.iterrows()):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem("" if pd.isna(value) else str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                table.setItem(row_index, col_index, item)
        table.resizeColumnsToContents()

    def show_error(self, message: str) -> None:
        """统一错误提示。"""
        self.log(f"错误：{message}")
        QMessageBox.warning(self, "提示", message)

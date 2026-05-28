# 数据分析与神经网络预测 Qt 桌面软件设计

## 目标

开发一款离线桌面端软件，用于 Excel 数据导入、预处理、统计分析、神经网络训练、预测和结果导出。第一版重点是建立稳定的项目架构和可运行闭环，后续可在不重写 UI 的前提下扩展更复杂的模型后端。

## 技术路线

- 界面框架：Qt 5.15，Python 绑定采用 PySide2。
- 数据处理：pandas、numpy。
- 统计与机器学习：scikit-learn。
- 图表：matplotlib 嵌入 Qt。
- Excel：openpyxl 处理 xlsx，xlrd 处理 xls，xlsxwriter/openpyxl 用于导出 xlsx。
- 模型保存：joblib。
- 打包：PyInstaller，优先 onedir 离线包。

选择 PySide2 的原因是它是 Qt for Python 官方路线，许可更适合桌面软件分发，并且能覆盖 Qt 5.15 的主窗口、信号槽、线程和控件需求。第一版模型后端采用 sklearn MLPRegressor，能快速完成训练、评估、loss 曲线、保存和预测闭环。

## 项目结构

```text
nn_qt/
  README.md
  pyproject.toml
  requirements.txt
  requirements-dev.txt
  .gitignore

  src/
    nn_qt/
      __init__.py
      __main__.py
      app.py
      config.py
      resources.py

      models/
        data_models.py
        train_models.py
        result_models.py

      services/
        data_service.py
        analysis_service.py
        training_service.py
        prediction_service.py
        model_store.py

      ui/
        main_window.py
        sidebar.py
        log_panel.py
        chart_widget.py
        data_page.py
        analysis_page.py
        train_page.py
        predict_page.py

      workers/
        train_worker.py
        predict_worker.py

      utils/
        exceptions.py
        validators.py
        logger.py

  tests/
    test_data_service.py
    test_analysis_service.py
    test_training_service.py
    test_prediction_service.py
    test_smoke_qt.py

  packaging/
    nn_qt.spec
    build.ps1
    build_offline.ps1
    prepare_wheels.ps1
    smoke_test.ps1
```

## UI 设计

主窗口使用 `QMainWindow`，左侧为 `SidebarWidget`，右侧为 `QStackedWidget` 主显示区，底部或右侧固定日志面板。

页面划分：

- 数据导入页：选择 Excel 文件，配置前 N 列为输入变量、后 M 列为输出变量，显示数据预览。
- 统计分析页：执行 PCA、ANOVA、灵敏度分析，显示结果表格和图表。
- 模型训练页：配置隐藏层、学习率、Epochs、测试集比例、归一化方式，启动训练并展示指标。
- 预测导出页：加载已保存模型，导入只有输入特征的新 Excel，导出预测结果。

UI 只负责参数收集、状态展示和信号连接，不直接依赖 pandas、sklearn 或 joblib。耗时任务通过 Worker 在线程中执行，避免界面卡顿。

## 数据流

1. 用户导入 Excel。
2. `DataService` 根据 N/M 列拆分为 features 和 targets。
3. `DataService` 执行数值转换、缺失值处理、标准化或归一化。
4. `AnalysisService` 基于处理后的输入输出执行 PCA、ANOVA 和灵敏度分析。
5. `TrainingService` 划分训练集和测试集，训练 MLPRegressor。
6. `ModelStore` 保存模型、scaler、列名顺序、训练配置和评估指标。
7. `PredictionService` 加载模型包，按训练时的特征列顺序重排新数据并预测。
8. 预测结果导出为 Excel，包含 `Predictions` 和 `ModelInfo` 两个 sheet。

## 核心数据模型

```python
ExcelLoadConfig:
  path
  sheet_name
  feature_count
  target_count

PreprocessConfig:
  missing_strategy
  scaler
  fill_value

TrainConfig:
  hidden_layers
  learning_rate
  epochs
  test_size
  random_state

DatasetBundle:
  raw
  X
  y
  feature_names
  target_names

TrainResult:
  model_package
  train_mse
  train_r2
  test_mse
  test_r2
  loss_curve
  y_test
  y_pred
```

## 统计分析策略

PCA：

- 对输入特征执行标准化后再 PCA。
- 输出前两个主成分散点图。
- 输出解释方差比柱状图。
- PCA 作为解释分析功能，不默认替代原始特征参与训练。

ANOVA：

- 使用 `f_regression`。
- 多目标时对每个 target 分别计算 F-value 和 p-value。
- 结果以 target x feature 的表格返回。

灵敏度分析：

- 第一版使用 RandomForestRegressor 的 feature_importances_。
- 多目标时提供总体重要性；后续可扩展为逐目标重要性和 permutation importance。
- 图表为特征重要性柱状图。

## 训练与预测策略

第一版使用 `MLPRegressor`。

训练参数：

- 隐藏层节点数：例如 `64,32` 解析为 `(64, 32)`。
- 学习率：大于 0 的浮点数。
- Epochs：正整数，对应 `max_iter`。
- 测试集比例：默认 0.2。

评估指标：

- MSE。
- R2。
- loss 曲线。
- 真实值 vs 预测值图。

模型包保存内容：

- sklearn 模型。
- X scaler。
- 特征列名和目标列名。
- 训练配置。
- 训练指标。
- loss 曲线。
- 创建时间和应用版本。

预测时必须按模型包保存的 `feature_columns` 重排输入列。缺失列、非数值数据和空值会返回清晰错误。

## 错误处理

统一定义业务异常，并将异常转换为日志区和弹窗提示。

关键错误场景：

- 文件不存在或格式不支持。
- N/M 列配置不合法。
- 数据中存在无法转换的非数值列。
- target 存在缺失值。
- Excel sheet 为空。
- 模型文件损坏或版本不兼容。
- 预测文件缺少训练时所需特征列。

## 测试策略

采用 pytest 先覆盖纯服务层，Qt UI 做基本 smoke test。

优先测试：

- Excel 读取和 N/M 列切分。
- 缺失值处理和 scaler 行为。
- PCA、ANOVA、灵敏度结果 shape。
- 隐藏层参数解析和校验。
- MLP 训练能输出 MSE、R2、loss。
- 模型保存后可加载，预测结果维度正确。
- 预测导出 Excel 能生成 `Predictions` 和 `ModelInfo` sheet。
- QApplication 和 MainWindow 能创建。

实现阶段遵循测试先行：先写服务层失败测试，再实现最小代码让测试通过。UI 骨架以 smoke test 和手动运行验证为主。

## 打包策略

第一版提供 PyInstaller onedir 打包脚本。

打包内容：

- 应用 exe。
- Qt platform plugins。
- assets 和 qss。
- pandas、sklearn、openpyxl、xlrd 等依赖。
- 离线部署说明。

离线依赖使用 wheelhouse：

- `prepare_wheels.ps1` 在联网环境下载 wheel。
- `build_offline.ps1` 在离线环境从 wheelhouse 安装依赖并打包。
- `smoke_test.ps1` 启动 exe 验证主窗口能打开。

## 第一版范围

包含：

- Qt 主窗口和多页面骨架。
- Excel 导入。
- N/M 列配置。
- 缺失值处理。
- StandardScaler 和 MinMaxScaler。
- PCA、ANOVA、随机森林灵敏度分析。
- MLPRegressor 训练。
- MSE、R2、loss、真实值 vs 预测值图。
- 模型保存和加载。
- 新 Excel 预测和导出。
- PyInstaller 打包骨架。
- 基础 pytest 测试。

暂不包含：

- PyTorch 或 GPU 训练。
- 数据库。
- 复杂报表系统。
- 自动特征工程。
- 多语言界面。
- 插件系统。

这些能力可在第一版闭环稳定后扩展。

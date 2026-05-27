# 数据分析与神经网络预测软件

本项目是一款面向离线桌面场景的数据分析与神经网络预测工具，使用 PyQt5 构建图形界面，结合 pandas、numpy、scikit-learn、statsmodels、matplotlib 与 seaborn 完成 Excel 数据导入、预处理、统计分析、模型训练、预测导出和 Windows 独立程序打包。

## 主要功能

- Excel 数据导入：支持 `.xlsx` 与 `.xls` 文件。
- 参数配置：支持设置前 N 列为输入变量 Features，后 M 列为输出变量 Targets。
- 数据预处理：缺失值处理、标准化 StandardScaler、归一化 MinMaxScaler。
- PCA 分析：输出前两个主成分散点图与方差解释率。
- ANOVA 方差分析：输出输入变量与目标变量的 F-value 和 p-value。
- 灵敏度分析：基于随机森林特征重要性或 permutation importance 评估输入变量影响程度。
- 神经网络训练：基于 scikit-learn MLPRegressor/MLPClassifier 的基础多层感知机模型。
- 模型评估：输出 MSE、R2 等指标，并绘制真实值 vs 预测值、Loss 曲线。
- 模型保存与预测：保存训练模型，导入新 Excel 特征数据后批量预测并导出结果。
- Windows 打包：通过 PyInstaller 生成隐藏控制台的独立 `.exe`。

## 建议目录结构

```text
.
├── README.md
├── environment.yml
├── requirements.txt
├── pyinstaller.spec
├── pyproject.toml
├── scripts
│   └── build_windows.bat
├── src
│   ├── main.py
│   └── nn_analysis_app
│       ├── app.py
│       ├── core
│       │   ├── analysis.py
│       │   ├── config.py
│       │   ├── data_io.py
│       │   └── modeling.py
│       └── ui
│           ├── main_window.py
│           ├── plot_canvas.py
│           └── workers.py
├── assets
├── resources
│   ├── icons
│   └── styles
├── examples
│   ├── sample_train.xlsx
│   └── sample_predict.xlsx
└── outputs
    ├── models
    ├── figures
    └── predictions
```

说明：

- `src/main.py`：PyQt 应用入口，等价于 `python -m nn_analysis_app`。
- `src/nn_analysis_app/core/`：数据处理、统计分析、模型训练、预测导出等核心逻辑。
- `src/nn_analysis_app/ui/`：主窗口、图表画布和后台任务封装。
- `assets/`、`resources/`：用于放置图标、样式表、默认配置等静态资源。
- `examples/`：用于放置示例 Excel，不建议提交敏感业务数据。
- `outputs/`：用于保存模型、图表、预测结果，可根据需要加入 `.gitignore`。

## Excel 使用流程

训练数据文件应按列组织，且尽量使用首行为字段名：

```text
feature_1 | feature_2 | ... | feature_N | target_1 | ... | target_M
```

1. 在软件中点击“导入 Excel”，选择 `.xlsx` 或 `.xls` 训练文件。
2. 设置“前 N 列作为输入变量”和“后 M 列作为输出变量”。
3. 选择缺失值处理策略，例如均值填充或删除缺失行。
4. 选择数据缩放方式，例如标准化或归一化。
5. 运行 PCA、ANOVA、灵敏度分析，查看输出表格与图表。
6. 配置 MLP 模型参数，例如隐藏层节点、学习率、Epochs。
7. 开始训练，查看 MSE、R2、真实值 vs 预测值图和 Loss 曲线。
8. 保存模型文件，用于后续离线预测。
9. 导入仅包含输入特征的新 Excel 文件，执行预测并导出新的 Excel 结果。

注意事项：

- `.xlsx` 依赖 `openpyxl`，`.xls` 依赖 `xlrd`。
- 训练数据和预测数据的输入特征列顺序必须一致。
- 文本列、日期列、类别列建议在导入后统一编码或转换为数值。
- 缺失值过多的列建议在训练前人工检查，避免模型学习到错误模式。

## Conda 环境创建

推荐使用 conda 创建隔离环境：

```bat
conda env create -f environment.yml
conda activate nn-analysis
```

如需使用 pip 安装：

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

在 macOS/Linux 上使用 pip 虚拟环境时，激活命令通常为：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 本地运行

源码完成后，可从项目根目录运行：

```bat
conda activate nn-analysis
python src\main.py
```

macOS/Linux：

```bash
conda activate nn-analysis
python src/main.py
```

也可以使用模块方式运行：

```bash
python -m nn_analysis_app
```

## Windows 打包说明

建议在 Windows 机器上完成 PyInstaller 打包，因为跨平台打包 `.exe` 通常不可行。推荐流程：

```bat
conda env create -f environment.yml
conda activate nn-analysis
scripts\build_windows.bat
```

打包脚本会执行：

```bat
pyinstaller --clean --noconfirm pyinstaller.spec
```

默认输出位置：

- `build/`：PyInstaller 中间文件。
- `dist/NeuralNetworkAnalysis/`：可分发的 Windows 应用目录。
- `dist/NeuralNetworkAnalysis/NeuralNetworkAnalysis.exe`：主程序。

### 隐藏控制台

`pyinstaller.spec` 中已设置：

```python
console=False
```

这会让 Windows GUI 程序运行时不显示黑色控制台窗口。如需调试启动日志，可临时改为 `console=True` 后重新打包。

### 静态资源

`pyinstaller.spec` 默认会尝试打包以下目录：

- `assets/`
- `resources/`
- `examples/`

如果项目中新增图标、样式、默认配置、模型模板等静态文件，请放入这些目录，或在 `pyinstaller.spec` 的 `datas` 中补充路径。

### 依赖注意事项

- PyQt5：PyInstaller 通常可自动收集 Qt 插件，但遇到平台插件缺失时，需要检查 `PyQt5/Qt5/plugins/platforms` 是否被正确打包。
- matplotlib：spec 中通过 `collect_data_files("matplotlib")` 收集字体、样式和后端资源。
- scikit-learn：spec 中通过 `collect_submodules("sklearn")` 补充动态导入模块，避免运行时报缺失 sklearn 子模块。
- statsmodels：spec 中通过 `collect_submodules("statsmodels")` 与 `copy_metadata("statsmodels")` 处理动态导入和包元数据。
- pandas/openpyxl/xlrd：用于 Excel 读写，发布前请用 `.xlsx` 与 `.xls` 样例分别测试。
- seaborn：依赖 matplotlib，打包后请测试绘图窗口和图表保存功能。

## 常见问题

**1. 打包后启动失败，提示缺少 sklearn 或 statsmodels 模块。**

先确认使用的是本项目的 `pyinstaller.spec`。如果仍失败，将报错中的模块名加入 `hiddenimports`。

**2. 打包后 matplotlib 中文乱码。**

请在程序中设置可用中文字体，例如 Microsoft YaHei、SimHei，并确认目标机器安装了对应字体。必要时可将字体文件作为静态资源打包。

**3. 读取 `.xls` 失败。**

确认已安装 `xlrd`。新版 `xlrd` 只支持 `.xls`，`.xlsx` 请使用 `openpyxl`。

**4. 预测 Excel 列数不匹配。**

预测文件必须只包含训练阶段定义的输入特征列，并保持列顺序一致。

## 交付与发布建议

- 发布前使用小型示例 Excel 完整跑通导入、预处理、分析、训练、保存模型、预测导出。
- Windows 打包后在一台未安装 Python 的机器上验证应用启动与核心功能。
- 如果模型文件、输出图表或预测结果较大，建议不要提交到 Git 仓库。

# 数据分析与神经网络预测

这是一个基于 Qt 的离线桌面端数据分析与神经网络预测软件骨架。

## 主要能力

- 导入 `.xlsx` / `.xls` 数据。
- 配置前 N 列为输入变量，后 M 列为输出变量。
- 缺失值处理、标准化和归一化。
- PCA、ANOVA、随机森林灵敏度分析。
- sklearn MLPRegressor 训练、评估、保存和加载。
- 导入新 Excel 执行预测并导出结果。
- PyInstaller 离线打包脚本骨架。

## 开发运行

```powershell
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = "src"
python -m nn_qt
```

当前环境使用 Qt5.15 的 PyQt5，并通过兼容层运行同一套界面骨架。Python 3.12 下 PySide2 通常没有可用 wheel，因此离线包默认采用 PyQt5。

## 测试

```powershell
python -m pytest -v
```

## 离线打包

联网环境准备 wheelhouse：

```powershell
.\packaging\prepare_wheels.ps1 -Python python
```

本机打包：

```powershell
.\packaging\build.ps1 -Python python
```

离线环境打包：

```powershell
.\packaging\build_offline.ps1 -Python python -WheelDir wheels\py312-win_amd64
```

如果是在发布包的 `source` 目录中重建，请使用发布包上一级的 wheelhouse：

```powershell
.\packaging\build_offline.ps1 -Python python -WheelDir ..\wheels\py312-win_amd64
```

第一版默认生成 onedir 目录，便于排查 Qt 插件、Excel 引擎和 sklearn 依赖问题。

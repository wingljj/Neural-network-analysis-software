# Conda 离线包部署说明

本项目支持使用 `conda-pack` 生成离线包。目标机器无需安装 Python 或 conda，软件仍然运行在打包好的 conda 环境中。

## 构建离线包

在联网构建机上执行：

```bash
conda activate nn-analysis
python scripts/build_offline_package.py
```

生成文件位于 `dist/`，例如：

```text
dist/NeuralNetworkAnalysis-offline-darwin-arm64.tar.gz
```

Windows 构建机上同样执行：

```bat
conda activate nn-analysis
python scripts\build_offline_package.py
```

## 离线机器启动

macOS/Linux：

```bash
tar -xzf NeuralNetworkAnalysis-offline-*.tar.gz
cd NeuralNetworkAnalysis-offline-*
./scripts/run_app.command
```

Windows：

```bat
解压 NeuralNetworkAnalysis-offline-windows-*.zip
进入解压目录
双击 scripts\run_app.bat
```

首次启动时脚本会自动解压 `runtime/*.tar.gz` 到 `runtime/env`，执行 `conda-unpack` 修复路径，然后启动软件。之后再次运行同一个脚本会直接打开软件。

## 平台限制

- `conda-pack` 不是跨平台打包工具。
- Windows 包必须在 Windows 上构建，macOS 包必须在对应架构的 macOS 上构建。
- macOS Intel 与 Apple Silicon 建议分别出包。
- 解压后不要随意移动整个目录；如果移动了，建议删除 `runtime/env` 后重新运行启动脚本。
- Windows 建议部署到短路径，例如 `C:\NNAnalysis`，避免路径过长或特殊字符影响 Qt、matplotlib、动态库加载。

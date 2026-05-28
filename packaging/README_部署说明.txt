数据分析与神经网络预测 - 离线部署说明

一、直接运行

1. 打开 app\nn_qt 目录。
2. 双击 nn_qt.exe 启动软件。
3. 若 Windows 安全提示拦截，请选择“更多信息”后允许运行。

二、目录说明

app\nn_qt\
  已打包好的桌面程序目录，nn_qt.exe 是主程序。

wheels\py312-win_amd64\
  Python 3.12 / Windows 64 位离线依赖 wheelhouse。

source\
  项目源码、测试、requirements 和打包脚本。需要重新构建时使用。

source\packaging\
  prepare_wheels.ps1：联网环境下载离线依赖。
  build.ps1：联网/本机环境构建程序。
  build_offline.ps1：离线环境从 wheelhouse 安装依赖并构建。
  smoke_test.ps1：启动 exe 做冒烟测试。

requirements.txt / requirements-dev.txt
  Python 依赖清单。

三、重新离线构建

在装有 Python 3.12 的 Windows 64 位机器上执行：

cd source
powershell -NoProfile -ExecutionPolicy Bypass -File packaging\build_offline.ps1 -Python python -WheelDir ..\wheels\py312-win_amd64

四、验证

可执行：

powershell -NoProfile -ExecutionPolicy Bypass -File source\packaging\smoke_test.ps1 -ExePath ..\app\nn_qt\nn_qt.exe

退出码为 0 表示主程序能启动。

五、注意事项

1. 当前离线包基于 Python 3.12 和 Qt5 / PyQt5 构建。
2. Qt 5.15 的 PySide2 在 Python 3.12 下通常没有可用 wheel，因此该包使用 PyQt5 5.15 运行同一套 Qt 界面。
3. 如果目标机器缺少 Microsoft Visual C++ Runtime，请安装 VC_redist.x64.exe 后再运行。
4. 本程序不依赖目标机器安装 Microsoft Excel。

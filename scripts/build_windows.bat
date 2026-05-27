@echo off
setlocal enabledelayedexpansion

REM Windows 一键打包脚本。
REM 建议在已激活的 conda 环境中执行：
REM   conda activate nn-analysis
REM   scripts\build_windows.bat

cd /d "%~dp0\.."

set APP_ENTRY=src\main.py
set SPEC_FILE=pyinstaller.spec

if not exist "%APP_ENTRY%" (
    echo [ERROR] 未找到入口文件 "%APP_ENTRY%"。
    echo [ERROR] 请确认源码已生成，或修改本脚本中的 APP_ENTRY。
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 未找到 python，请先激活 conda 环境：
    echo         conda activate nn-analysis
    exit /b 1
)

where pyinstaller >nul 2>nul
if errorlevel 1 (
    echo [INFO] 未找到 pyinstaller，正在通过 pip 安装 requirements.txt 中的依赖。
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

echo [INFO] 清理历史打包产物...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [INFO] 开始 PyInstaller 打包，隐藏控制台窗口并收集静态资源与科学计算依赖...
pyinstaller --clean --noconfirm "%SPEC_FILE%"
if errorlevel 1 (
    echo [ERROR] 打包失败，请检查上方 PyInstaller 日志。
    exit /b 1
)

echo [OK] 打包完成。
echo [OK] 输出目录：dist\NeuralNetworkAnalysis
echo [OK] 主程序：dist\NeuralNetworkAnalysis\NeuralNetworkAnalysis.exe

endlocal

@echo off
setlocal

REM Windows 离线包启动脚本。
REM 优先使用离线包内置 conda 环境；如果不存在，则回退到本机 nn-analysis 环境。

cd /d "%~dp0\.."
set PACKED_ENV=%CD%\runtime\env

if not exist "%PACKED_ENV%\python.exe" (
    for %%F in ("%CD%\runtime\*.tar.gz") do set ENV_ARCHIVE=%%~fF
    if defined ENV_ARCHIVE (
        echo [INFO] 首次启动，正在解压内置 conda 环境...
        if not exist "%PACKED_ENV%" mkdir "%PACKED_ENV%"
        tar -xzf "%ENV_ARCHIVE%" -C "%PACKED_ENV%"
        if exist "%PACKED_ENV%\Scripts\conda-unpack.exe" (
            "%PACKED_ENV%\Scripts\conda-unpack.exe"
        )
        echo [OK] 内置 conda 环境准备完成。
    )
)

if exist "%PACKED_ENV%\python.exe" (
    "%PACKED_ENV%\python.exe" "%CD%\src\main.py"
    exit /b %ERRORLEVEL%
)

where conda >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 未找到离线环境，也未找到本机 conda。
    echo [ERROR] 请先创建环境：conda env create -f environment.yml
    exit /b 1
)

conda run -n nn-analysis python "%CD%\src\main.py"
exit /b %ERRORLEVEL%

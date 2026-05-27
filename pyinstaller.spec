# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置。

使用方式：
    pyinstaller --clean --noconfirm pyinstaller.spec

说明：
    1. 默认入口文件为 src/main.py。
    2. 默认打包 assets/、resources/ 与 examples/ 静态目录，目录不存在时会自动跳过。
    3. console=False 用于隐藏 Windows 控制台窗口。
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata


ROOT = Path(SPECPATH)
APP_NAME = "NeuralNetworkAnalysis"
ENTRY_SCRIPT = ROOT / "src" / "main.py"


def existing_data_dir(relative_path: str, target_name: str):
    """仅在静态资源目录存在时加入 datas，避免骨架阶段打包配置报路径错误。"""
    source = ROOT / relative_path
    if source.exists():
        return [(str(source), target_name)]
    return []


datas = []
datas += existing_data_dir("assets", "assets")
datas += existing_data_dir("resources", "resources")
datas += existing_data_dir("examples", "examples")

# matplotlib 需要字体、样式和后端资源；statsmodels 部分功能依赖包元数据。
datas += collect_data_files("matplotlib")
datas += copy_metadata("statsmodels")
datas += copy_metadata("scikit-learn")

hiddenimports = []

# sklearn、statsmodels 存在较多运行期动态导入，显式收集可降低打包后缺模块风险。
hiddenimports += collect_submodules("sklearn")
hiddenimports += collect_submodules("statsmodels")

# Excel、绘图和 Qt 相关模块在不同机器上偶尔会因动态导入遗漏，保守补充。
hiddenimports += [
    "openpyxl",
    "xlrd",
    "matplotlib.backends.backend_qt5agg",
    "matplotlib.backends.backend_agg",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
]


a = Analysis(
    [str(ENTRY_SCRIPT)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "pytest",
        "IPython",
        "notebook",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

SPEC_DIR = Path(SPECPATH).resolve()
ROOT_DIR = SPEC_DIR.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

block_cipher = None

hiddenimports = [
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "matplotlib.backends.backend_qtagg",
    "sklearn.neural_network._multilayer_perceptron",
    "sklearn.ensemble._forest",
    "sklearn.feature_selection._univariate_selection",
    "sklearn.decomposition._pca",
    "openpyxl",
    "xlrd",
    "xlsxwriter",
    "joblib",
]

datas = []

a = Analysis(
    [str(SRC_DIR / "nn_qt" / "__main__.py")],
    pathex=[str(ROOT_DIR), str(SRC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "IPython",
        "jedi",
        "sphinx",
        "docutils",
        "numba",
        "llvmlite",
        "black",
        "notebook",
        "nbformat",
        "zmq",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="nn_qt",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="nn_qt",
)

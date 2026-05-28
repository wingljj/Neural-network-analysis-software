"""Qt 兼容层。

生产环境优先使用 PySide2；本地测试环境若只有 PyQt5，也可运行同一套 Qt5 界面骨架。
"""

from __future__ import annotations

try:  # pragma: no cover - 取决于本机 Qt 绑定安装情况
    from PySide2 import QtCore, QtGui, QtWidgets

    Signal = QtCore.Signal
    Slot = QtCore.Slot
    QT_BINDING = "PySide2"
except ModuleNotFoundError:  # pragma: no cover - 当前测试机走 PyQt5 回退
    from PyQt5 import QtCore, QtGui, QtWidgets

    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    QT_BINDING = "PyQt5"

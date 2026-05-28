"""资源路径工具。"""

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    """返回开发态项目根目录。"""

    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    """兼容开发态和 PyInstaller 打包态的资源路径。"""

    base = Path(getattr(sys, "_MEIPASS", project_root()))
    return base.joinpath(*parts)

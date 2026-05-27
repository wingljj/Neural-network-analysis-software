"""生成基于 conda-pack 的离线部署包。

离线包内容：
    1. 项目源码与启动脚本。
    2. 当前平台的 nn-analysis conda 环境压缩包。
    3. install_offline 脚本，用于在目标机器离线解压环境。

注意：conda 环境和 PyQt/NumPy 等二进制依赖强相关平台，macOS 生成的包
只能在相同架构的 macOS 上使用，Windows 包需要在 Windows 上生成。
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build" / "offline_package"
DEFAULT_ENV = "nn-analysis"


def run(command: list[str], cwd: Path | None = None) -> None:
    """执行命令，失败时直接抛出异常。"""
    print("[RUN]", " ".join(command))
    subprocess.run(command, cwd=cwd or ROOT, check=True)


def copy_project_files(package_dir: Path) -> None:
    """复制离线包运行所需的源码和配置文件。"""
    include_files = [
        ".gitignore",
        "README.md",
        "environment.yml",
        "OFFLINE_DEPLOY.md",
        "requirements.txt",
        "pyinstaller.spec",
        "pyproject.toml",
    ]
    include_dirs = ["src", "scripts", "tests", "assets", "resources", "examples"]

    for relative in include_files:
        source = ROOT / relative
        if source.exists():
            target = package_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    for relative in include_dirs:
        source = ROOT / relative
        if source.exists():
            target = package_dir / relative
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    "*.egg-info",
                    ".pytest_cache",
                    ".DS_Store",
                ),
            )


def write_install_scripts(package_dir: Path, env_archive_name: str) -> None:
    """写入离线安装脚本，目标机器无需联网即可解压环境。"""
    install_sh = package_dir / "install_offline.sh"
    install_sh.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
ENV_ARCHIVE="${{ROOT_DIR}}/runtime/{env_archive_name}"
ENV_DIR="${{ROOT_DIR}}/runtime/env"

mkdir -p "${{ENV_DIR}}"
tar -xzf "${{ENV_ARCHIVE}}" -C "${{ENV_DIR}}"
if [ -x "${{ENV_DIR}}/bin/conda-unpack" ]; then
    "${{ENV_DIR}}/bin/conda-unpack"
fi
chmod +x "${{ROOT_DIR}}/scripts/run_app.command"
echo "[OK] 离线环境已安装：${{ENV_DIR}}"
echo "[OK] 启动：scripts/run_app.command"
""",
        encoding="utf-8",
    )
    install_sh.chmod(0o755)

    install_bat = package_dir / "install_offline.bat"
    install_bat.write_text(
        f"""@echo off
setlocal
cd /d "%~dp0"
set ENV_ARCHIVE=%CD%\\runtime\\{env_archive_name}
set ENV_DIR=%CD%\\runtime\\env

if not exist "%ENV_DIR%" mkdir "%ENV_DIR%"
tar -xzf "%ENV_ARCHIVE%" -C "%ENV_DIR%"
if exist "%ENV_DIR%\\Scripts\\conda-unpack.exe" (
    "%ENV_DIR%\\Scripts\\conda-unpack.exe"
)
echo [OK] 离线环境已安装：%ENV_DIR%
echo [OK] 启动：scripts\\run_app.bat
endlocal
""",
        encoding="utf-8",
    )

    (package_dir / "OFFLINE_DEPLOY.md").write_text(
        f"""# 离线部署说明

此目录是“数据分析与神经网络预测软件”的 conda 离线部署包。

## 重要限制

- conda 环境包含平台相关二进制依赖，不能跨系统/架构使用。
- macOS arm64 生成的包只能给 macOS arm64 使用；Windows 包请在 Windows 上生成。
- 目标机器无需联网，但需要能解压 tar.gz；Windows 10/11 默认带 `tar`。

## 安装与启动

macOS/Linux：

```bash
./install_offline.sh
./scripts/run_app.command
```

Windows：

```bat
install_offline.bat
scripts\\run_app.bat
```

内置环境压缩包：`runtime/{env_archive_name}`。
""",
        encoding="utf-8",
    )


def pack_conda_env(env_name: str, package_dir: Path) -> Path:
    """使用 conda-pack 打包指定环境。"""
    runtime_dir = package_dir / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    env_archive = runtime_dir / f"{env_name}-{platform.system().lower()}-{platform.machine().lower()}.tar.gz"
    run(
        [
            "conda",
            "run",
            "-n",
            env_name,
            "conda-pack",
            "-n",
            env_name,
            "-o",
            str(env_archive),
            "--force",
            "--ignore-editable-packages",
        ]
    )
    return env_archive


def make_archive(package_dir: Path) -> Path:
    """把离线包目录再压缩成一个可分发归档。"""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_base = DIST_DIR / package_dir.name
    if platform.system().lower() == "windows":
        archive_path = shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=package_dir.parent,
            base_dir=package_dir.name,
        )
    else:
        archive_path = shutil.make_archive(
            str(archive_base),
            "gztar",
            root_dir=package_dir.parent,
            base_dir=package_dir.name,
        )
    return Path(archive_path)


def build(env_name: str) -> Path:
    """构建离线包并返回最终归档路径。"""
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    package_name = f"NeuralNetworkAnalysis-offline-{platform.system().lower()}-{platform.machine().lower()}"
    package_dir = BUILD_DIR / package_name
    package_dir.mkdir(parents=True)

    copy_project_files(package_dir)
    env_archive = pack_conda_env(env_name, package_dir)
    write_install_scripts(package_dir, env_archive.name)
    archive_path = make_archive(package_dir)
    print(f"[OK] 离线包已生成：{archive_path}")
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 conda 离线部署包")
    parser.add_argument("--env", default=DEFAULT_ENV, help="要打包的 conda 环境名")
    args = parser.parse_args()

    try:
        build(args.env)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] 命令执行失败：{exc}", file=sys.stderr)
        return exc.returncode
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] 离线包构建失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
set -euo pipefail

# macOS/Linux 离线包启动脚本。
# 本脚本会优先使用离线包内置 conda 环境；如果不存在，则回退到本机 nn-analysis 环境。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PACKED_ENV="${ROOT_DIR}/runtime/env"

if [ ! -x "${PACKED_ENV}/bin/python" ]; then
    ENV_ARCHIVE="$(find "${ROOT_DIR}/runtime" -maxdepth 1 -name '*.tar.gz' -print -quit 2>/dev/null || true)"
    if [ -n "${ENV_ARCHIVE}" ]; then
        echo "[INFO] 首次启动，正在解压内置 conda 环境..."
        mkdir -p "${PACKED_ENV}"
        tar -xzf "${ENV_ARCHIVE}" -C "${PACKED_ENV}"
        if [ -x "${PACKED_ENV}/bin/conda-unpack" ]; then
            "${PACKED_ENV}/bin/conda-unpack"
        fi
        echo "[OK] 内置 conda 环境准备完成。"
    fi
fi

if [ -x "${PACKED_ENV}/bin/python" ]; then
    PYTHON_BIN="${PACKED_ENV}/bin/python"
elif command -v conda >/dev/null 2>&1; then
    PYTHON_BIN="$(conda run -n nn-analysis python -c 'import sys; print(sys.executable)')"
else
    echo "[ERROR] 未找到离线环境，也未找到本机 conda。"
    echo "[ERROR] 请先创建环境：conda env create -f environment.yml"
    exit 1
fi

cd "${ROOT_DIR}"
exec "${PYTHON_BIN}" "${ROOT_DIR}/src/main.py"

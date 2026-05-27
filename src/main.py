"""兼容 PyInstaller 与源码运行的主入口。

开发运行：
    python src/main.py

包运行：
    python -m nn_analysis_app
"""

from nn_analysis_app.app import main


if __name__ == "__main__":
    raise SystemExit(main())


# Windows 一键打包说明：
# 1. 推荐先创建并激活 conda 环境：
#       conda env create -f environment.yml
#       conda activate nn-analysis
# 2. 在 Windows 项目根目录执行：
#       scripts\build_windows.bat
#    或直接执行：
#       pyinstaller --clean --noconfirm pyinstaller.spec
# 3. pyinstaller.spec 已建议设置 console=False，用于隐藏 GUI 程序启动时的黑色控制台。
# 4. 若新增图标、样式、示例 Excel、默认配置等静态资源，请放入 assets/、resources/
#    或 examples/，并同步加入 pyinstaller.spec 的 datas。
# 5. scikit-learn、statsmodels、matplotlib、PyQt5 存在动态导入或运行期资源，
#    pyinstaller.spec 中应通过 collect_submodules/collect_data_files 显式收集。

# UI Polish And Export Paths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the Qt desktop UI with a readable white theme, publication-style matplotlib charts with Chinese font support, and file/folder chooser workflows for model and prediction paths.

**Architecture:** Keep styling centralized in a small theme module and keep chart drawing inside `ChartWidget`. UI pages own file dialog buttons and emit the same existing signals, while `MainWindow` keeps workflow orchestration and model save behavior.

**Tech Stack:** Python, Qt5 via `qt_compat`, matplotlib, pandas, pytest, PyInstaller.

---

## Tasks

### Task 1: White Theme And Readable Fonts

**Files:**
- Create: `src/nn_qt/ui/theme.py`
- Modify: `src/nn_qt/app.py`
- Modify: `src/nn_qt/ui/main_window.py`
- Modify: `src/nn_qt/ui/sidebar.py`
- Test: `tests/test_ui_polish.py`

- [ ] Write tests asserting global font size, white sidebar QSS, adaptive sidebar width, and row height.
- [ ] Run targeted tests and confirm they fail against the current dark fixed-size sidebar.
- [ ] Implement centralized theme helpers, adaptive sidebar sizing, and white QSS.
- [ ] Run targeted tests and confirm pass.

### Task 2: Publication-Style Charts And Chinese Font Support

**Files:**
- Modify: `src/nn_qt/ui/chart_widget.py`
- Modify: `src/nn_qt/ui/main_window.py`
- Test: `tests/test_chart_widget.py`
- Test: `tests/test_qt_smoke.py`

- [ ] Write tests rendering Chinese text and negative values without missing glyph warnings.
- [ ] Write tests for loss, PCA, ANOVA, and sensitivity plotting methods.
- [ ] Run targeted tests and confirm they fail against default matplotlib behavior.
- [ ] Move plot drawing into `ChartWidget`, configure matplotlib font fallback and paper-style axes.
- [ ] Run targeted tests and confirm pass.

### Task 3: File Chooser Workflows

**Files:**
- Modify: `src/nn_qt/ui/predict_page.py`
- Modify: `src/nn_qt/ui/train_page.py`
- Modify: `src/nn_qt/ui/main_window.py`
- Test: `tests/test_path_dialogs.py`

- [ ] Write tests monkeypatching `QFileDialog` to validate browse/save buttons fill paths.
- [ ] Write tests asserting prediction input selection auto-fills output path.
- [ ] Write tests asserting saving a model fills predict page model path.
- [ ] Run targeted tests and confirm fail against current hand-typed paths.
- [ ] Implement browse/save buttons, read-only path fields, default output names, and model save backfill.
- [ ] Run targeted tests and confirm pass.

### Task 4: Verification And Offline Package Refresh

**Files:**
- Modify: `release/nn_qt_offline_package.zip`
- Modify: `release/nn_qt_offline_package/`

- [ ] Run `python -m pytest -v`.
- [ ] Run `.venv-build\Scripts\python.exe -m pytest -v`.
- [ ] Rebuild with `.venv-build\Scripts\python.exe -m PyInstaller packaging\nn_qt.spec --noconfirm --clean`.
- [ ] Run `packaging\smoke_test.ps1` against the rebuilt exe.
- [ ] Recreate `release\nn_qt_offline_package` and zip.

## Self-Review

Coverage: all requested issues are covered: white UI, larger adaptive sidebar text, publication-style charts, Chinese font rendering, and file chooser workflows.

Placeholder scan: no placeholders.

Type consistency: page signal signatures stay compatible with `MainWindow`; file dialog helpers only alter UI path entry behavior.

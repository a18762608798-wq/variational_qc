# variational_qc

变分量子计算实验项目独立仓库（从 `sync` 的 `theory/physics/quant_comp/04_project` 分离）。

## 目录

- `variational_qc_v0.1.0/`：早期探索版本（task1–task10）
- `variational_qc_v0.2.0/`：SSH-XXZ 实验 01–04（Julia + Python 双实现）
- `variational_qc_v0.3.0/`：当前主线（`doc/paper-outline.md` + `doc/expriment-map.md`，见 `PAPER_STATUS.html` / `EXPERIMENT_STATUS.html`）

## 追踪规则

- 忽略：`data/`、`*.npz`、`*.pdf`、各类缓存（`__pycache__`、`.pytest_cache` 等）、本地环境（`.CondaPkg/`、`node_modules/`）
- 保留：`*.png`（论文插图，`figs/` 下直接入库）

## 环境

- Julia 项目：各版本目录下 `Project.toml`，用 `CondaPkg.toml` 管理 Python 依赖
- Python 绘图：`scripts/figure_style.py`（Okabe-Ito / Tol 配色，colorblind-safe）

# variational_qc

变分量子计算实验项目：SSH-XXZ 自旋链的基态、序参量与 VQE 研究。

## 内容

- `src/`：数值核心（Julia）
  - `Shared01/`：哈密顿量、基态求解、数据读写
  - `Exp01/`：约化密度矩阵与 ZTilde 序参量
  - `Exp02/`：弦序、关联函数与面板数据
  - `Exp03/`：能隙求解、截面基组与交叉拟合
  - `Exp04/`：变分拟设、初态与 VQE 循环
- `scripts/`：`run_*.jl`（实验运行）、`verify_*.jl`（结果校验）、
  硬件任务提交（`exp05_*`、`exp06_*`）与论文绘图（`plot_*.py`）
- `specs/`：exp01–exp06、shared-01 的 spec / plan / tasks
- `docs/`：`paper-outline.md`、`expriment-map.md`、理论笔记（`docs/theory/`）
- `figs/`：论文插图（`*.png`）
- `test/`：`runtests.jl` 及相关测试
- `PAPER_STATUS.html` / `EXPERIMENT_STATUS.html`：论文与实验进度总览
  （浏览器在线查看：[PAPER_STATUS](https://a18762608798-wq.github.io/variational_qc/PAPER_STATUS.html) /
  [EXPERIMENT_STATUS](https://a18762608798-wq.github.io/variational_qc/EXPERIMENT_STATUS.html)）

## 追踪规则

- 忽略：`data/`、`*.npz`、`*.pdf`、各类缓存（`__pycache__`、`.pytest_cache` 等）、本地环境（`.CondaPkg/`、`node_modules/`）
- 保留：`*.png`（论文插图）

## 环境

- Julia：`Project.toml`，`CondaPkg.toml` 管理 Python 依赖
- Python 绘图：`scripts/figure_style.py`（Okabe-Ito / Tol 配色，colorblind-safe）

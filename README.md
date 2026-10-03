# variational_qc

变分量子计算实验项目（从 `sync` 的 `theory/physics/quant_comp/04_project` 分离）。

当前工作区即主线（原 `variational_qc_v0.3.0` 已提至根目录）：
`doc/paper-outline.md` + `doc/expriment-map.md`，进度见
`PAPER_STATUS.html` / `EXPERIMENT_STATUS.html`。

## 目录

- `src/`：Exp01–Exp04 + Shared01（Julia）
- `scripts/`：`run_*.jl`、`verify_*.jl`、硬件提交与绘图脚本
- `specs/`：exp01–exp06、shared-01 的 spec/plan/tasks
- `doc/theory/`：H、ansatz、cost_fun、gap、psi0、readout_mitigation、topological_op
- `figs/`：论文插图（`*.png` 入库）
- `test/`：`runtests.jl` + 硬件本地测试

## 追踪规则

- 忽略：`data/`、`*.npz`、`*.pdf`、各类缓存（`__pycache__`、`.pytest_cache` 等）、本地环境（`.CondaPkg/`、`node_modules/`）
- 保留：`*.png`（论文插图）

## 环境

- Julia：`Project.toml`，`CondaPkg.toml` 管理 Python 依赖
- Python 绘图：`scripts/figure_style.py`（Okabe-Ito / Tol 配色，colorblind-safe）

## 旧版本（v0.1.0 / v0.2.0）

已移出工作区，仅保留在 git 历史中。查看：

```bash
git log --oneline -- variational_qc_v0.2.0 | head
git show 3cd71a6:variational_qc_v0.2.0/Project.toml
```

注：`scripts/xcheck_v02.jl` 引用了已移出的 `variational_qc_v0.2.0/src_jl`，
如需运行，先 `git checkout 3cd71a6 -- variational_qc_v0.2.0` 取回旧树。

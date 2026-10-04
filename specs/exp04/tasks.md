# Tasks: exp04 模拟机 VQE

**Feature:** exp04

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

## Implementation

- [x] T001 实现 `src/Exp04/InitStates.jl`：`psi_triv/psitopo/psiafm`
  （`256` 维，基矢约定运行时断言 S01 同字符串）；`src/Exp04.jl` 父模块。
  完成条件：模块可加载，三态范数/`Z_tot`/`X̄`/`R` 构造性正确（由 T007 锁定）。
- [x] T002 实现 `src/Exp04/Ansatz.jl`：`L=8` 轨道/子层元数据（奇 `2` 轨、
  偶 `2` 轨，子层顺序按初态 `F/S`）与 `apply_circuit!`（单键 `4×4` 比特对作用）；
  `nparams`（`δ=0` 减半结构式）、零参数恒等。
  完成条件：单键酉与 kron 参考一致，零参数即初态（由 T007 锁定）。
- [x] T003 实现 `src/Exp04/VQELoop.jl`：`energy`（`H` 期望，`H` 只读自
  `Shared01.Hamiltonian`）、`pshift_gradient`（参数移位精确梯度）、
  `run_leg`（`64+1` 采样 + 前 `4` L-BFGS + 收敛旗/种子记录）、
  `run_point`（三路 + 同路链式 warm `p=2,3` + 取最小路）。
  完成条件：smoke 点（`δ=0/0.85 × s=0.01/0.5/0.99`）可出三路全收敛结果（由 T007 锁定）。
- [x] T004 实现 `src/Exp04/Store.jl`：按 `δ` 分块 `.npz` + 完成表续算；
  组装 `exp04_S06.npz`（三路全量 + 最小路 + 观测量）与 `exp04_S03.npz`
  （`594` 组同值引用）+ `exp04_manifest.json`（schema `exp04/v1`）。
  完成条件：中断续算一致（删块重跑组装不变）。
- [x] T005 编写 `scripts/run_exp04.jl`（模块 API → 分块落盘 → 组装；
  顺序 `δ=0 → 0.85`）并执行全点生产（`198` 点 × 三路 × `p` 链）。
  完成条件：S06/S03 文件 + manifest 落盘，形状与网格定义一致。
- [x] T006 出图与示意：`scripts/plot_S06.py`（4 诊断图 `(δ × {S(π), string})`，
  每图 `p=1,2,3` 三线，mathtext 标签，`figure_style.py` 风格，
  矢量 PDF + 300dpi PNG 落 `figs/exp04/`）与 `scripts/plot_D06.py`
  （拟设示意图，同目录）。
  完成条件：坐标系自检通过，四图顺序正确，D06a–c 人工保真核对通过，
  附 skill 风格检查报告块。

## Validation

- [x] T007 单元测试（`test/runtests.jl` 追加，全绿）：初态三性；
  单键酉 kron 一致；零参数恒等；参数移位梯度 vs 有限差分；
  `δ=0` 参数计数；warm 链 smoke 单调；非法输入拒绝路径。
- [x] T008 生产断言（`scripts/verify_exp04.jl`，对正式输出全量执行）：
  `E* ≤ E_init + 1e-8`；守恒量三项容限内；收敛旗全真或棘轮接受
  （`stagnant` 仅 `p>1`，且 `dE_tail` 与棘轮不等式由存档值重算锁定）；
  `a*` 为最小路；
  `E* ≥ E0 − 1e-8`（暴力精确交叉）；
  S03 形状 `594` 组且与 S06 同值；无缺失、无 NaN。

## Follow-up (重编号：D06→D06a–c 三分相 + S06；诊断图保留)

- [x] T009 扩展 `scripts/plot_D06.py` 出 D06a–c 三分相示意图（每相初态 +
  所需拟设电路；triv/afm 首动偶子层、topo 首动奇子层；只画 ansatz.md
  已定义元素）并实跑出图（`figs/exp04/exp04_D06{a,b,c}.pdf/.png`）。
  完成条件：脚本零数据输入，三图可出图，`figure_style.py` 风格。
- [ ] T010 人工保真核对 D06a–c（用户目检：初态/轨道配对/子层顺序/`p` 堆叠
  与 ansatz.md、psi0.md 一致，无虚构门）。
  完成条件：用户确认通过。

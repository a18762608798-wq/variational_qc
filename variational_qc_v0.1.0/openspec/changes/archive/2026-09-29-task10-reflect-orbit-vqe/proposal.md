# Proposal

## Why

均匀子层共享拟设（task3 单层、task4 多层 2–5 层）在过渡区存在可观测的表达缺口，但 `doc/qc/evolution_qc.md` 已定义的反射对称 orbit 参数（link 独立、每轨道继承 `(θ_1,θ_2)` 分工、单层 8 参数）从未在模拟机上验证。本 change 在浅层（1–3 层、`δ=±1` 切线）定量回答 orbit 参数是否改善能量贴合与 `Z_R`/`Q` 相落点，为后续是否推广到深层或真机提供依据。

## What Changes

- 新增 `task10_reflect_orbit/` 任务目录（配置 + 脚本 + 逐深度 `data/interim` + `data/figures`），不改动 task1/3/4 既有产物：
  - orbit 拟设实现：按 `doc/qc/evolution_qc.md` 反射对称 orbit 分组（`O_out={(0,1),(6,7)}`、`O_in={(2,3),(4,5)}`、`E_out={(1,2),(5,6)}`、`E_c={(3,4)}`），每轨道继承 `S_z` 守恒的 `(θ_1,θ_2)` 分工（`XX+YY` 共 `θ_1`、`ZZ` 独立 `θ_2`），单层 8 参数，深层每层 8 参数（1/2/3 层共 8/16/24 参数）；GHZ 初态下首层 2 个 `θ_2`（每 orbit 各一）退化为整体相位，剩 6 有效参数；
  - 子层顺序与初态配对沿用 task3 约定（平庸 `U_oU_e`、拓扑 `U_eU_o`、GHZ 取 `U_oU_e`），三初态（triv/topo/afm）保持不变，拟设始终待在 `P=-1` 扇区，代价函数为裸 `H` 的 statevector 精确期望，不引入采样噪声；
  - 扫描范围：`L=8 OBC`、`depths={1,2,3}`、`δ=±1`、`s∈[0,1]` 51 点均匀网格（共 102 行，行序 `delta` 外层、`s` 内层，与 task3/4 同契约）；
  - 优化策略：depth1 全局+polish 两步优化（pilot 定预算），depth2/3 由浅层最优 warm-start 递推（垫底+微扰+polish，pilot 门控）；
  - 获胜 thetas 纯后处理派生 `Q_vqe` / `ZR_vqe`（与 task3 同定义，不重跑优化）；
  - 输出图形：逐深度 × 逐 `δ` 三张画布——`min(VQE-orbit)` vs 解析 `E0/E1`、orbit `Q` vs 解析 `Q`、orbit `Z_R` vs 解析 `tilde_Z_R`（3 深度 × 2 δ × 3 类 = 18 组 PNG 必选 + PDF 可选同名）。

## Capabilities

### New Capabilities

- `numerics/vqe-reflect-orbit-sweep`: 反射对称 orbit 参数拟设的构造、1–3 层 warm-start 扫描存档（目标值 CSV + thetas）与 `Q/ZR` 纯后处理派生契约。

### Modified Capabilities

- `viz/vqe-comparison`: 追加 orbit 逐深度画布组需求（每深度每 δ 三画布：min-energy 三线、Q 双线、ZR 双线；标题与文件名含 orbit 与深度标识，不得与既有 uniform/nosym 画布混淆）。

## Impact

- 只新增 `task10_reflect_orbit/` 目录与本 change 的 delta specs；task1 解析谱/`Q`/`tilde_Z_R` CSV 仅作只读对照输入，不改动其表头与行序；
- 复用 `shared/numerics` 算子定义与 `shared/viz` 绘图语言（能量绝对值、`Q∈[-1,1]`、`tilde_Z_R∈[-1.2,1.2]`），不引入新依赖（Qiskit statevector + SciPy 优化栈与 task3/4 一致）；
- 结论仅覆盖模拟机浅层 orbit 效应，不推广到深层 scaling 或真机 penalty；若 pilot 显示 orbit 无增益或优化不稳定，按门控砍深度集合而非强行全量。
- 作废声明：本 change 曾按旧版 doc（每键单转角、单层 4 参数）实现并产出 depth1 全套数值产物与部分 depth2 ckpt，`doc/qc/evolution_qc.md` 修正为单层 8 参数后，上述产物全部作废（已删除），不作为任何结论依据；新数据以 `seed_base=20260929` 命名空间隔离。

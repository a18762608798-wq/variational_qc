# Design

## Context

- 现状：task3（单层 uniform 4 参数 `XX/YY` 共用 + `ZZ` 独立）与 task4（多层 uniform 2–5 层 warm-start 递推）已覆盖均匀拟设；`shared/viz/plot_vqe.py` 与 task3 `observables.py`/`zr_obs.py` 定义了能量/Q/ZR 的派生与绘图语言；task1 解析谱 CSV 为只读对照。
- 约束：见 proposal（`L=8 OBC`、`δ=±1`、`s` 51 点、102 行 CSV 契约、statevector 精确、P stays −1）；orbit 定义以 `doc/qc/evolution_qc.md` 为准，单层 8 参数（4 轨道 × `(θ_1,θ_2)`，`S_z` 守恒分工逐 orbit 继承），不得与 uniform theta 混用或互相递推。
- 本设计只定方法与目录骨架，不复述 specs 的行为契约。

## Goals / Non-Goals

**Goals:**

- 给出 orbit 拟设到 1–3 层扫描、派生、绘图的可复用骨架，使 specs 的每个 SHALL 都有唯一落点。
- 锁定 warm-start 递推链与确定性要求，避免实现时发明第二套口径。

**Non-Goals:**

- 不决定 pilot 的具体预算数值（由 pilot 结论锁定，specs 已门控）。
- 不做深层（≥4）scaling、不做真机、不改 task1/3/4 产物与主 specs。

## Decisions

### 1. 目录骨架镜像 task4，按深度隔离

`task10_reflect_orbit/{config,scripts,depth1,depth2,depth3}`，每深度 `data/interim/{vqe_L8_OBC.csv,vqe_thetas.json,vqe_Q_L8_OBC.csv,vqe_ZR_L8_OBC.csv,sweep_ckpt.json}` + `data/figures/`；`config/grid.toml` 声明 `depths=[1,2,3]`、网格与路径模板。备选（单目录混存多深度）否决：与 task4 既有 figures 按深度隔离的惯例冲突，且文件名易与 uniform 混淆。

### 2. orbit 拟设独立新文件，复用初态与哈密顿量

新增 `scripts/ansatz_orbit.py`（不改 task3/4 的 `ansatz.py`）：复用三初态制备（`init_triv/topo/afm`）与 `H_matrix(s,delta)` 语义，新增 orbit 分组常量（`O_OUT/O_IN/E_OUT/E_C`）与双角子层（同 orbit 键 `RXX(θ_1)RYY(θ_1)` 共 `θ_1` + `RZZ(θ_2)` 独立 `θ_2`）；`build_vqe_circuit(init, x, n_layers)` 每层 8 参数（`o_out1,o_out2,o_in1,o_in2,e_out1,e_out2,e_c1,e_c2`），首层保持初态配对顺序、层间交替。备选（在 uniform `ansatz.py` 加分支）否决：两套参数语义不同（8 数/层 vs 4 数/层），分支易导致 depth2 误用 uniform thetas 递推；独立文件使 `assert len(x)==8*k` 与递推来源检查可强制执行。

### 3. 优化链：depth1 全局+polish，depth2/3 浅层递推

depth1 复用 task3 两步模式（`differential_evolution` 全局 + `COBYLA` polish，θ∈[0,2π)，8 维；两档预算起点 light `{de_maxiter=30, popsize=15, cobyla=300}` vs base `{50, 20, 500}`，由 pilot 数据锁定）；depth2/3 复用 task4 `warm_start` 模式（上一深度同点最优垫底 + 确定性微扰多 restart + polish，劣于垫底则钳位回垫底并记录，新层垫 8 参数）。`seed_base=20260929`（与 task3/4 及作废的 4 参数版数据都不重叠）并单线程 BLAS 保证逐位确定性（含跨进程，派生禁用内置 `hash`）；微扰尺度初值 0.3、restart 数初值 3，最终以 pilot 结论为准。GHZ 初态首层 2 个 `θ_2` 为平坦方向（整体相位），实现 SHALL NOT 将其 seed 极差计为失败。备选（各深度独立全局优化）否决：24 参数全局预算爆炸且破坏深度单调可审计性。

### 4. Q/ZR 纯后处理复用，不重实现算子

`derive_orbit_qzr.py` 从本任务 `vqe_thetas.json` 取逐点 argmin 获胜 `(init,x)`，重建 orbit 电路求 statevector，直接 import task3 `observables.Q_of_state` 与 `zr_obs.tilde_ZR_of_state`。备选（拷贝算子进 task10）否决：双份定义必然漂移；复用使"与解析同语言"的对照有效。

### 5. 绘图复用既有语言，仅加 orbit 标识

复用 `shared/viz/plot_vqe.py` 的三类画布（min-energy 三线 / Q 双线 / ZR 双线、纵轴语言不变），`plot_orbit.py` 只做数据源切换（本任务 CSV + task1 解析 CSV）与标题/文件名 orbit+深度标识（如 `vqe_min_comparison_deltam1_orbit_depth2`）。备选（新绘图风格）否决：跨任务对照（orbit vs uniform）要求同语言画布。

## Risks / Trade-offs

- [Risk] 8 维 DE 单点成本数倍于 4 维，全量时间需重估（pilot 实测后再定 depth2/3 是否全跑）→ Mitigation：pilot 先行、门控砍深度集合；specs 要求如实呈现偏离，不得调参掩盖。
- [Risk] warm-start 钳位（劣于垫底回垫底）掩盖优化器退化 → Mitigation：specs 要求深度单调性如实审计，钳位触发率记入结论并复核。
- [Risk] orbit（8 数/层）与 uniform（4 数/层）维度不同但同属 thetas JSON，误用（跨任务递推）仍可能 → Mitigation：递推来源硬检查（depth2 必须读本任务 depth1 thetas，维度 `8k` 断言），实现任务中列为必查项；`seed_base=20260929` 与作废数据命名空间隔离。
- [Risk] GHZ 首层 2 个 `θ_2` 平坦方向导致 seed 极差虚高 → Mitigation：specs 已豁免该两方向的极差判定；验收时单独记录，不计失败。
- [Trade-off] 限定 1–3 层：深层 orbit 效应留白，换取 pilot 预算可控与 18 张画布的评审闭环；深层扩展为后续 change，不在本设计内。

# Design: vqe-spectra-delta-pm1

## Context

`doc/qc/` 已锁定物理定义：三初态制备方式、`U_eU_o` 单层 4 参数拟态（`S_z` 守恒、`P=−1` 扇区内）、代价函数用裸 `H`。解析对照线现成：`task1_baseline/data/interim/spectra_L8_OBC.csv`（`δ=±1` × 201 点 `E0/E1`）。画图沿用 `shared/viz/` 的原子写出与确定性约定。动机见 proposal.md。

## Goals / Non-Goals

- Goals：新目录（如 `task3_vqe/`）内跑通"初态→拟态→两步优化→CSV→八图"全链；pilot 先定预算再全量。
- Non-Goals：不加层数（单层；多层是后续 change）；不做 shots 噪声（statevector 精确）；不存波函数/优化轨迹（只存目标值）；不动 task1/task2 产物与既有 specs。

## Decisions

1. **新顶层任务目录**（如 `task3_vqe/`，自带 `data/{interim,figures}` + 配置）：VQE 是 Python 生态（Qiskit），与 Julia 求解链无代码复用，独立目录最干净；只复用解析 CSV 做对照输入。备选（塞进 task1/task2 目录）被否决：污染既有任务边界。
2. **Qiskit Aer `method='statevector'` 精确期望**：一次电路执行即得精确 `⟨H⟩`（`H` 按 Pauli 分解求和或 `SparsePauliOp.expectation`），无 shots 参数；优化目标函数确定性，seed 只影响优化器起点。备选（qasm shots）被否决：噪声会淹没 1e-2 量级劈裂细节，属后续 change。
3. **全局 `scipy.differential_evolution`（bounds `[0,2π)^4`）+ 局部 COBYLA（或 BFGS）polish**：转角天然有界，全局步不需要边界技巧；scipy 无额外依赖。GHZ 初态浪费一个参数（doc 已述）不特殊处理——优化器自行压平冗余方向。
4. **pilot 先行定预算**：3~5 个 `s` 点 × 三初态（`δ=+1` 为主，含简并区点），报告"预算-最优值"收敛曲线与多 seed 极差；全量预算取"极差 < 1e-6 且 polish 增益饱和"的最小档。备选（固定大预算一步到位）被否决：烧电且无依据。
5. **输出一 CSV 宽表**（`s,delta,E_triv,E_topo,E_afm`，102 行）：画图一次读入即得 3 线，避免多文件 join；失败点不填数、整体失败（spec 契约）。
6. **并行**：各 `(s,δ,init)` 点独立，多进程池并行（seed 按坐标确定性派生，保证"同 seed 两次逐位一致"）。
7. **min 三线图为纯后处理**：读同一 VQE 宽表逐行取最小，不碰优化链；画图入口扩展模式或复用渲染函数，文件名与五线图隔离（如 `vqe_min_comparison_*.png`）。
8. **VQE-Q 派生亦为纯后处理**：获胜 `(init, seed)` 由 thetas 逐点 argmin 确定（与 CSV 最优值一致）；`O_str`/`S(π)` 实现为 LSB 序 Z-对角矩阵，先经 bit-reverse 在 Julia 存档态上与 task1 CSV 交叉验证，再用于 VQE 态；Q 双线图纵轴 `[-1,1]` 与 task1 Q 图同语言。
9. **VQE-ZR 派生同模式**：约化密度矩阵路线（`ρ_I`、`R_I` 镜像交换、两半纯度），LSB 序实现，格点映射由 Julia 存档交叉验证锁定；ZR 双线图纵轴取物理带 `[-1.2,1.2]`。

## Risks / Trade-offs

- [Risk] 某相区单层拟态表达不够，VQE 线系统性高于 `E0` → Mitigation：这本身就是结论（spec 场景已写"偏离记为结论"）；变分上界性（`E_init ≥ E0−1e-6`）是优化正确性的硬门，违反则判失败重跑/加预算。
- [Risk] `differential_evolution` 预算不足导致坏点 → Mitigation：pilot 定预算 + 多 seed 极差监控；坏点判据是上界性违反，可定位到坐标。
- [Risk] Qiskit 版本 API 漂移 → Mitigation：`CondaPkg.toml` 钉版本范围，pilot 即验证 API 可用。
- [Trade-off] statevector 无硬件噪声，结论只关于表达能力 → Mitigation：接受，proposal 已限定；shots/噪声是后续 change。

## Migration Plan

纯新增目录与依赖；删目录即回滚。`CondaPkg.toml` 加 `qiskit`、`qiskit-aer` 后 pixi env 重建（pilot 即验证）。

## Open Questions

无。

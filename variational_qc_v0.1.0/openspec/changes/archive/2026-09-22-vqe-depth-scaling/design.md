# Design: vqe-depth-scaling

## Context

task3 已沉淀：三初态制备、`U_e/U_o` 单层 4 参数、statevector 精确期望、两步优化（DE + COBYLA，light 预算）、thetas 全存档（含单层 306 格点 × 3 seed）、Q/ZR 派生链（Julia 交叉验证过）、画图三 mode。解析对照线现成（spectra、`Q`、`tilde_ZR` CSV）。动机见 proposal.md。

## Goals / Non-Goals

- Goals：新任务目录内跑通 depth2→5 逐层递推（warm-start），每深度 6 张图 + thetas 链不断。
- Non-Goals：不碰 task1/task2/task3 产物与结论；不做 shots 噪声；不做全量全局重搜（warm-start 已定）；不存波函数。

## Decisions

1. **新顶层任务目录**（如 `task4_vqe_depth/`，下设 `depth{2,3,4,5}/data/{interim,figures}` + 一份网格/优化配置）：深度是最大内聚边界，目录隔离后 task3 的 8 张图零混淆；备选（task3 下加子目录）被否决：污染已归档的单层 baseline。
2. **`ansatz` 加 `n_layers` 参数**：层块复用单层子层函数，层间顺序逐层交替、首层保持初态配对；`n=1` 必须与 task3 单层逐位一致（spec 回退场景覆盖）。其余脚本（优化、派生、画图）以 theta 向量长度参数化，逻辑零改动。
3. **warm-start 递推**：depth `k` 起点 = depth `k−1` 同点最优 theta 垫底 + 微扰（尺度由 pilot 定，如 `0.1~0.3 rad` 量级均匀扰动），3 组微扰 seed 确定性派生，COBYLA polish；depth2 由 task3 thetas 递推。备选（每深度全量 DE 重搜）被否决：贵 3-5 倍，且 warm-start 的 diabatic 偏置与"跟踪分支"的物理图像自洽。
4. **pilot 门控 depth2 与 depth5**：报告微扰尺度-增益曲线、多 seed 极差、单点耗时；depth3/4 预算插值；任一 pilot 不通过（极差不收敛或耗时超预算）则砍深度集合，不强行全量。
5. **Q/ZR 派生照搬 task3 链**：获胜 thetas → 重建电路 → 既有算子 → 逐深度 Q/ZR CSV；算子实现复用（`observables`、`zr_obs`），无需重新交叉验证（同一套矩阵；多层只改变输入态）。
6. **画图复用三 mode**：输出路径按深度隔离（如 `depth2/..._depth2.png` 或深度子目录），文件名含深度标识；min-energy 不画分初态线（已定）。

## Risks / Trade-offs

- [Risk] warm-start 把 diabatic 偏置焊死，深层永远跳不出浅层分支 → Mitigation：微扰尺度是逃逸机制，pilot 监控"深层最优 vs 浅层垫底"增益分布；若全线零增益，结论即"2-5 层无改进"，本身可发表，不算失败。
- [Risk] 20 参数 COBYLA polish 陷入平坦区，耗时爆炸 → Mitigation：pilot 先测 depth5（最难）；超时则降 polish 预算或砍深度。
- [Risk] thetas 链断裂（某深度某点全失败）→ Mitigation：增量 checkpoint + 失败非零退出；下游深度缺起点则该点标记、整体失败，不静默跳过。
- [Trade-off] 无全量全局重搜，深层最优性只有 warm-start 证据 → Mitigation：接受，proposal 已限定；spec 的"深度单调性可审计"场景负责抓退化。

## Migration Plan

纯新增目录；删目录即回滚。无新增依赖。

## Open Questions

无。

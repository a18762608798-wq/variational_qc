# Design

## Context

- `03_tools_practice/qmeas` 已有完整 benchmark 管线（见 exploration）：`benchmark/topology.py`（拓扑快照+缓存+死比特过滤+4 种扩展策略）、`circuits.py`（线性 cluster 制备+稳定子分组+读出校验）、`runner.py`（async 并发提交/轮询+逐份 checkpoint）、`scoring.py`（稳定子均值+读出保真度）、`io.py`（跨机排序+报告）。task6 不造轮子，只做配置、执行与存档。
- 运行环境：系统 python 无 quark/qmeas；task6 复用 `03 qmeas` 项目 env python（已含 quarkstudio、quarkcircuit、qmeas editable），不另建环境。
- 物理池很小：精确枚举（DFS）得 Baihua 254、Shenglian 558 条无向 8 链——"连接稀疏采不满"的旧假设被证伪，实际是准一维结构下长链天然稀少，但 500/1000 上限仍从不截断；反转视为同一物理链，去重后全覆盖。

## Goals / Non-Goals

**Goals:**

- 两机最优 8 比特链 + 全候选 evidence，一次性、可复现、可续跑。
- 提交前账单可见、人工确认；token 不落盘。

**Non-Goals:**

- 不改 qmeas 库本身（发现 bug 则另起 change 修）。
- 不做 Dongling；不做其他链长；shots 不加码、不做复测轮（见 Decisions）。
- 不跑任何变分电路——本任务只选链。

## Decisions

- **复用 qmeas benchmark，不 fork**：管线已覆盖采样→提交→打分→报告全链路，且 checkpoint/节流等真机残酷现实都已处理。fork 只会分叉维护。task6 侧只放配置脚本与产物。
- **sample 上限 1000 有向链/机（兜底用）**：sample 内部采 `配额×4` 候选再截前 N；上限提到 1000 只为保证 Shenglian 去重后不饿肚子，实际物理池（254+558）远小于上限，上限永不截断有效链。替代：conservative/slide（只测种子邻域，违背"最彻底"要求）——否决。
- **shots=1024（不加复测）**：云端最小单位即 1024；8 稳定子平均后统计噪声 ~0.01，而好坏链分差通常 ≥0.1（坏链稳定子直接塌）。替代：top-N 高 shots 复测——精度收益小、多一轮排队等待，否决；若实测首名分差 <0.02，报告中标注"并列"，留给后续 change 处理。
- **权重沿用 0.8/0.2**：被测电路以 H+CZ 制备为主，稳定子天然是 CZ 保真度探针，读出只占辅助位。用户已确认。
- **task6 目录归属 variational_param，解释器复用 qmeas env**：推荐报告是后续真机 VQE 的输入，放项目内顺手；qmeas 侧只留库代码。执行时核实发现 qmeas 项目 env 已含全部依赖且子目录 CondaPkg 无独立 Project 不生效，故 task6 不另建环境，直接用 qmeas env python（路径见 task6 README），避免重复 resolve 与版本漂移。
- **无向去重 + 小池全覆盖（路2）**：精确枚举（DFS）证实两机物理池很小——Baihua 254、Shenglian 558 条无向 8 链；旧方案 survivors 反向孪生率 ~100%，约一半机时测的是同一条链的反转。去重规则 `min(链, 反转)` canonical，cluster 制备与稳定子集在反转下不变故物理等价。采样上限提到 1000 有向链兜底（保证 Shenglian 去重后不饿肚子），预期 bill 约 812×4×1024 ≈ 333 万 shots，比旧 3952 任务还少。`build_chains`（qmeas 库）不动，去重只做在 task6 prescreen 侧。
- **静态预筛只做减法**：阈值只卡"明显烂"（死比特、边保真度 `< 0.9`），不做加权排名——静态分与实测表现只假设正相关到"烂链翻盘概率极低"的程度；全覆盖后预筛省钱有限，但保留作卫生过滤。
- **一次性全提交再统一轮询（防插队）**：旧 runner 逐链串行（提交4→等4→下一条），745 链约 4 小时且每波重排队会被插队。改为两阶段：先把全部缺失电路一次提交完，再统一轮询。平台侧提交限流由既有 `submit_retries` 指数退避吸收；真被限流则自然降速，不分波。例外：本条需改 qmeas `runner.py` 主循环（原 design"不 fork/不动库"让路——改动仅限提交编排，电路/打分/checkpoint 语义不变，checkpoint 文件格式不变故已产出的 11 条结果零损失复用）。
- **提交当天 force 重拉拓扑**：缓存用于离线预览省请求，真机提交必须基于最新校准快照（`calibration_time` 进报告）。

## Risks / Trade-offs

- [一次性提交触发平台限流] → 2980 任务同时在途，提交侧由 `submit_retries=6` 指数退避吸收 transient 限流；若平台硬性拒收则降为自然降速重试，绝不分波重排（防插队优先）。
- [预筛误杀] → "静态丑但实测美"的链（串扰/漂移吃个例）可能被阈值误砍：阈值只卡明显烂（边保真度 `< 0.9`），被剔除清单进报告备查；真机结果若显示 survivors 整体偏弱，另起 change 放宽重测。
- [有效链过少] → 某机有效 8 链 <5 时"选最优"退化为矮子拔将军：如实记录候选总数与全部分数，不硬选，报告标注。
- [排队超时] → runner 有 poll_timeout/重试/重提；checkpoint 保证已拿结果不丢，超时任务人工看账单后决定补测或放弃。
- [校准漂移] → 提交与测量的 calibration_time 全进 evidence；若两机校准时间差数天，跨机比较仅供参考，报告标注。
- [qmeas 环境差异] → task6 的 CondaPkg 与 qmeas 自带 CondaPkg 对齐版本；先离线预览验证 import 与拓扑拉取，再谈提交。

## Migration Plan

不适用（新增任务目录，无存量迁移）。归档后主 specs 新增 `hardware/qubit-chain-select`。

## Open Questions

- 无。shots 复测阈值（0.02）为报告标注规则，不改变 specs/approach/tasks，真机见分晓。

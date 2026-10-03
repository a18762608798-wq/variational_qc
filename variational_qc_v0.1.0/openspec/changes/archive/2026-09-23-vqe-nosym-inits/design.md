# Design: vqe-nosym-inits

## Context

task3/4 已沉淀：子层配对惯例、两步优化与 warm-start  machinery、Q/ZR 派生链（Julia 交叉验证过）、画图三 mode、增量 checkpoint、单线程 BLAS 确定性。`doc/qc/initial_state.md` 真机简化版锁定新初态定义。解析对照线现成。动机见 proposal.md。

## Goals / Non-Goals

- Goals：新任务目录内跑通 nosym depth1（全局优化）→ depth5（直跳 warm-start）链，每深度 6 张图 + thetas 链。
- Non-Goals：不动 task1~4 产物与结论；不做 shots 噪声；不跑中间深度；不改拟态门结构（只换初态）。

## Decisions

1. **新顶层任务目录**（如 `task5_vqe_nosym/`，下设 `depth{1,5}/data/{interim,figures}` + 配置）：初态定义变了就是新任务；备选（task4 下加分支）被否决：task4 已归档且其 thetas 链是"对称初态"语义，混入 nosym 会污染 warm-start 递推源。
2. **初态函数新增 nosym 分支**：triv 复用对称版（文档声明一致）；topo-nosym 为 bulk 三单态 + `|00⟩_{0,7}`（`0,7` 无门）；AFM-nosym 为奇数位 X（无 H、无 CNOT）。子层配对惯例沿用（topo 仍奇键先）以保可比性，尽管 `(0,7)` 非单态后"首层给相位"的理由弱化——如实记录。
3. **depth1 沿 task3 路线**（DE 全局 + polish，同量级预算先行、pilot 校准）；**depth5 直跳**：起点 = 本任务 depth1 同点最优 + 16 参数微扰（尺度 pilot 实测），3 restart 取最优 + polish；深层以下不差于垫底（钳位逻辑复用 task4）。
4. **P 期望降级为记录项**：拟态保 `P` 但初态不在扇区内，`P` 期望逐点存档供分析（如 thetas 附带字段或独立诊断 CSV），不断言 `−1`；`H/H'` 等价性不再引用，对照基准只用解析 `E0`。
5. **Q/ZR 派生与画图照搬 task4**：获胜 thetas → 既有算子 → 逐深度 CSV；画布标题与文件名加 nosym 标识。

## Risks / Trade-offs

- [Risk] nosym 初态掉出好 basin，全线系统性偏高 → Mitigation：这本身就是待量化的代价（spec 场景已写"均为结论"）；变分上界门照常抓优化失败。
- [Risk] 16 维直跳微扰尺度失配（太小焊死、太大退化成随机重搜）→ Mitigation：pilot 实测尺度-增益曲线； depths 只有两端，无插值风险。
- [Risk] 子层配对惯例对 nosym 非最优 → Mitigation：接受，可比性优先；真要换配对是后续 change。
- [Trade-off] 只要 1 和 5，缺失中间深度的 scaling 曲线 → Mitigation：接受，depth1/5 两端已能回答"简化代价在深浅两端各是多少"；中间深度后续可补。

## Migration Plan

纯新增目录；删目录即回滚。无新增依赖。

## Open Questions

无。

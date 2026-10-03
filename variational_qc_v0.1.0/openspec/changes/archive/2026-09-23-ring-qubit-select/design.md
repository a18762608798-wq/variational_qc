# Design

## Context

- `03_tools_practice/qmeas` benchmark 已有 ring 全套支撑（exploration 已核实）：`topology.find_rings`（DFS 全枚举 + 最小节点起点 + 旋转/翻转归一，只收偶数长度）、`circuits.build_circuits(n, ring=True)`（闭合 CZ + 模 n 稳定子 + 奇偶两组断言）、`runner` 按 `config.shape` 切 coupling（含闭合边）与电路集、`config.shape` 校验（ring 限偶数长）。
- task6 留下可复用的全部经验：qmeas env 复用、两阶段提交（转译限流16/提交信号量/轮询50）、resume 不重提、stale 清理脚本、Failed 需经 query 发现（轮询器缺口仍在）。
- 离线枚举已出：Baihua 4 环、Shenglian 9 环（0 秒出结果），池子极小。

## Goals / Non-Goals

**Goals:**

- 两机 13 环全测 + 独立环推荐，一次性、可复现、可续跑。
- 提交前账单可见、人工确认；token 不落盘。

**Non-Goals:**

- 不改 qmeas 库（沿用 ring 管线；发现 bug 另起 change）。
- 不做其他环长；shots 不加码；不与链混排比较。
- 不跑任何变分电路——本任务只选环。

## Decisions

- **全枚举全测，不采样**：池子 13 环，`max_chains_per_chip` 设 1000 兜底永不截断；bill 约 13×4×1024 ≈ 5.3 万 shots。替代： sampling——池子比采样配额还小，无意义，否决。
- **权重/shots 沿用链任务**：`0.8/0.2` + 1024。环制备多 1 个 CZ 且稳定子全三体，分数预计整体低一档（预期内）；调权重会破坏与链的可比性，否决。
- **task7 对齐 task6 结构**：config（grid.toml 加 `shape="ring"`）+ scripts（preview/prescreen/submit/cancel_stale 照搬，改名链→环）+ data + README/ANALYSIS。解释器复用 qmeas env。
- **提交当天 force 重拉拓扑**：环枚举对拓扑敏感（一条边 calibration 变化可增删环），必须基于最新快照；`calibration_time` 进报告。
- **沿用 task6 的提交编排**：两阶段全提交（防插队）、轮询并发 50、有 tid 不重提。转译量仅 52 个电路，无线程爆炸之忧。

## Risks / Trade-offs

- [环池随校准变化] → 提交当天重枚举为准，离线数（4+9）仅供参考；环数变化如实进报告。
- [排队超时] → runner poll_timeout/重试/重提 + checkpoint 续跑；超时任务人工看账单后补测或放弃。
- [Failed 空转] → task6 已知缺口：`result()` 对 Failed 回 `{}`，轮询不自知；收尾时 query Failed 对账，单条 cancel+去 tid 重跑。
- [环链不可比] → 报告与 ANALYSIS 明确标注环内比较；跨形状比较留给后续研究。

## Migration Plan

不适用（新增任务目录，无存量迁移）。归档后主 specs 新增 `hardware/ring-qubit-select`。

## Open Questions

- 无。

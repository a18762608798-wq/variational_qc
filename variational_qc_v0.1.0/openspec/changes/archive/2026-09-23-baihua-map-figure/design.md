# Design

## Context

- quark `Backend.draw` 的 `save_svg_fname` 在 Agg 无头环境静默失败（已实证），且 `highlight_nodes` 只支持单组节点高亮、无边高亮——满足不了三类标记需求，故自绘。
- 数据源：`task6_qubit_select/data/topology_cache/Baihua_*.json`（本地缓存，`qubits_info.coordinate` + T1 + `couplers_info.fidelity`）。
- 标记集来自已落盘结论：task6 冠军链、task7 4 环与各环最佳 8-子链（ANALYSIS 表）。

## Goals / Non-Goals

**Goals:**

- 一张图讲清位置关系；离线可复现；英文标注。

**Non-Goals:**

- 不做交互式；不画 Shenglian（本次只要 Baihua）；不动 qmeas 库。

## Decisions

- **官方图拦截+叠加，不自绘**：`save_svg_fname` 在 Agg 下静默失败（实证：全盘无文件），但拦截 `plt.show` 可拿到官方 figure（其主 axes 数据坐标与拓扑快照一致），直接在其上画三类标记后 `savefig`。替代：纯自绘（已验证可行，但官图边保真度编号/T1色标更权威）——改用官方底图。
- **快照而非实时拉取**：图是结论配图，必须与选链时的校准快照一致；标题写死校准时间，换快照重跑即新图。
- **英文标注**：无头环境无 CJK 字体，中文全变方框（已踩坑）。

## Risks / Trade-offs

- [快照过期] → 图只对应当次校准负责；标题校准时间即版本声明。
- [标记极简] → 只标三个最优（最好链/最好环/环中最好链），不标前几名：
  图面干净，结论唯一；其余候选只活在 JSON 里。

## Migration Plan

不适用（新增脚本与产物）。归档后主 specs 新增 `viz/baihua-topology-map`.

## Open Questions

- 无。

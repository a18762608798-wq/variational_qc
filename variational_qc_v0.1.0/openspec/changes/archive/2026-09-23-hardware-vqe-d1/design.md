# Design

## Context

- task3（sym）/task5（nosym）的 depth-1 获胜 thetas 与 thetas 存档已落盘；
  task1 解析谱（E0/E1/Q）为对照基线；task6/task7 给出 Baihua 冠军链与
  最优环（含各环最佳 8-子链表）。
- qmeas benchmark 管线（两阶段提交、checkpoint、resume 不重提、stale 清理、
  Failed 对账）经 task6/7 实战可用；本任务测量电路走同一提交器，
  只是电路内容换成 VQE 拟态 + 三基旋转。
- H 的 qubitwise 分组：XX 键一组、YY 键一组、ZZ 键一组 → X/Y/Z 三基；
  Q 与 P 两项的 Z-对角部分搭 Z 基便车（见 exploration 结论）。

## Goals / Non-Goals

**Goals:**

- 612 点真机 H/Q 全收回，与 Aer/解析三线对照，量化硬件 penalty。
- 一次提交、断点续跑、原始计数全存档。

**Non-Goals:**

- 不做真机优化（任何优化器都不上）；不测 ZR；δ=0 以后再加；
  不改 qmeas 库。

## Decisions

- **零优化纯前向**：Aer 最优点即终点；真机只执行不搜索。替代：真机
  COBYLA polish（每点多 ~40 evals ≈ 7 万任务，噪声下 polish 收益不明）——
  否决，留给后续 change。
- **一次全交约 1836 任务**：同校准窗口可比；thetas 是死的，无需中场调整。
  沿用两阶段提交（防插队）+ 轮询 50 并发。
- **读出纠错打开**：quark 平台侧 `correct`（与选链裸测不同；VQE 要的是
  尽量准的能量，mitigation overhead 平台承担）。原始计数仍全存，
  可回退裸分析。
- **sym-topo 桥接**：逻辑 0/7 经桥比特 `{125,138}` 三跳 SWAP 连接
  （`139-138-125-126`）；桥比特不参与拟态，只做 0-7 单态制备的通道。
  SWAP 深度代价如实进误差，不特殊处理。
- **转译 O3 + coupling pin 死**：optimization_level=3，basis_gates
  `["rz","rx","ry","cz"]`；coupling_map 按映射给（链线性 8、环闭合 10），
  不给转译器自由选映射的余地（task6/7 同款做法，已验证 CZ 数只减不增）。
  桥 SWAP 走 ring 邻接边，转译不得绕路。
- **提交当天验存活**：冠军链 8 比特 + 环 10 比特任一死亡即停，
  不降级、不换比特（换比特则与 Aer theta 的物理对应全乱）。

## Risks / Trade-offs

- [校准漂移] → 提交与测量的 calibration_time 全进 evidence；thetas 是死的，
  漂移只影响结论不影响执行。
- [排队超时] → checkpoint + resume 不重提；超时按 task6/7 流程补测或放弃。
- [Failed 空转] → 收尾 query Failed 对账（已知缺口），单条重跑。
- [桥 SWAP 噪声] → sym-topo 点天然多 ~6 个 CNOT；与链任务点不可比，
  只与自身 Aer 值比（penalty 含桥代价，如实记录）。

## Migration Plan

不适用（新增任务目录）。归档后主 specs 新增 `hardware/vqe-forward-d1`。

## Open Questions

- 无。

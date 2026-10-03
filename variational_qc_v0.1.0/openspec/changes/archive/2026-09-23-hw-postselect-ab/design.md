# Design

## Context

- 输入：`task8_hardware_vqe/data/checkpoints/` 612 文件，只读不写回。
- 方案源：`doc/postselect/postselect.md`（A 洗 O/S/Q、B 洗 H、三批独立
  shot 无联合筛、H_post 非上界）。
- task8 的 `analysis.py`（H/Q/P 合成）与 `plot_vqe.py`（full/min/q/o/s）
  全部复用；后选择 = 在合成前加一道计数过滤。
- M 定义：8 逻辑比特中 1 的个数为 4（端序与 task8 一致：
  反转后第 j 位为逻辑 j）。

## Goals / Non-Goals

**Goals:**

- A+B 后选择版 CSV + 四组画布 + 保留率诊断，体例与 task8 一致。

**Non-Goals:**

- 不重测、不重算裸值；不碰 ZR；不改 task8 任何文件。

## Decisions

- **过滤即子集**：A = Z 直方图丢 M≠0 项后走原合成函数；B = 三基各按
  宇称丢项后走原 H 合成。不写新估计算法，只加过滤器——数学复用
  task8 已验证路径。
- **winner 按 H_post 重定**：Q/O/S 的获胜初态取 H_post argmin
  （explore 已确认）；保留率诊断独立存 `retention.csv`
 （列：s,delta,task,init,frac_z_M0,frac_x_even,frac_y_even）。
- **空集记 NaN 不中断**：极端噪声点可能筛空；画布跳过 NaN 点不断线
  （pandas 默认行为，验收时确认）。
- **task9 目录对齐 task8**：config+scripts+data+README/ANALYSIS；
  ANALYSIS 写 A/B 对比结论（洗完相变锐化多少、保留率塌在哪）。

## Risks / Trade-offs

- [保留率过低] → 某相保留率 <10% 时误差棒爆炸：数值照出，
  ANALYSIS 如实标注，不隐藏。
- [H_post 被误读为上界] → 画布标题与 CSV 附注双声明"诊断量"。
- [NaN 断线误读] → 验收看图确认断线处与保留率 CSV 对得上。

## Migration Plan

不适用（新增任务目录）。归档后主 specs 新增 `hardware/postselect-ab`。

## Open Questions

- 无。

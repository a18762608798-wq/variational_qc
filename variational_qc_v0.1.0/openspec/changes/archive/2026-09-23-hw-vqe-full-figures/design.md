# Design

## Context

- `shared/viz/plot_vqe.py --mode full` 已存在（task3 用过）：读 VQE 三列 CSV
  + task1 spectra，画 E0/E1 + 三线。task8 sym/nosym E CSV 表头均与 task3 同形
  （`s,delta,E_triv,E_topo,E_afm`），直接复用，零新代码。
- task8 sym/nosym 数据已落盘（各 102 行），无需真机、无需重算。

## Goals / Non-Goals

**Goals:**

- δ=±1 两张 full 画布，与 task3 Aer 版并排可比。

**Non-Goals:**

- 不改绘图器；不碰数据。

## Decisions

- **复用 plot_vqe 不新增脚本**：表头同形，`--mode full` 开箱即用；
  标题/文件名带 hw+{sym,nosym}+δ 标识，与既有 task8 画布命名体系统一。

## Risks / Trade-offs

- [无实质风险] → 纯已落盘数据后处理；输入缺列时绘图器非零退出，
  不产残缺图片。

## Migration Plan

不适用。归档后主 specs `viz/vqe-comparison` 追加本需求。

## Open Questions

- 无。

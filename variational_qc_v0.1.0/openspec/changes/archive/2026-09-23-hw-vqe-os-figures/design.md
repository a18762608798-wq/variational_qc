# Design

## Context

- `Q_from_counts` 已返回 `(q, o_norm, s_norm)`；`derive_hw.py` 当前丢弃后两项。
  加四列是纯输出扩展，合成数学不变。
- task1 解析线：`Ostr_L8_OBC.csv` / `Spi_L8_OBC.csv` 已落盘（需先核对表头
  与行序，再定绘图器读法）。
- `plot_vqe.py` 现有 `--mode {full,min,q,zr}`；O/S 需新模式。
- figures/ 现有 16 张（min/q/full × sym/nosym × δ，PNG+PDF 为 32 文件）。

## Goals / Non-Goals

**Goals:**

- O/S 四列 CSV + 8 张对照图 + figures 分类，三件事一次做完。

**Non-Goals:**

- 不重算、不重测；不动已有 CSV/图的内容与文件名语义。

## Decisions

- **OS 列进新 CSV，不动旧表头**：旧 CSV 已被验收与引用，加列有碎表风险；
  新文件 `vqe_{sym,nosym}_OS_L8_OBC.csv` 干净。
- **plot_vqe 加 `o`/`s` 模式**：与 q/zr 同构（解析 CSV + 真机 CSV + δ 切片），
  复用标题/落盘/确定性逻辑；不另起绘图脚本。
- **搬图只换目录不改名**：`min/q/full/os` 四子目录；搬后列清单核对
  32 文件数一致，无散文件残留。

## Risks / Trade-offs

- [解析线表头不对齐] → 先读 `Ostr/Spi` 表头再写绘图调用；对不上就停下问，
  不猜格式。
- [搬图断引用] → 本项目内无代码引用 figures 绝对路径（画布均为终端产物）；
  搬后清单核对即可。

## Migration Plan

不适用。归档后主 specs `viz/vqe-comparison` 追加本需求。

## Open Questions

- 无。

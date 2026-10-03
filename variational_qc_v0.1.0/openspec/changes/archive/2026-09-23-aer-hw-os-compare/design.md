# Design

## Context

- Aer thetas：task3（sym）/task5 nosym depth-1（`vqe_thetas.json`，含 E），
  statevector 精确 O/S 导出路径 verify_aer (a2) 已验证。
- 真机 O/S：task9 `vqe_{sym,nosym}_OS_L8_OBC.csv`（winner 口径：H_post
  argmin；注意 Aer winner 口径是裸 E argmin——两者 winner 初态可能不同，
  三线对比时按各自 winner 画，不强行对齐；ANALYSIS 如实标注分歧点）。
- 解析线：task1 `Ostr/Spi`（`O_str_norm`/`S_pi_norm` 列）。
- `plot_vqe.py` o/s 模式现画 2 线，需加第三线（Aer）。

## Goals / Non-Goals

**Goals:**

- Aer O/S CSV + 8 张三线图，表达缺口 vs 硬件 penalty 可分读。

**Non-Goals:**

- 不画 min/Q/full；不重测；不动 task8/9 任何文件。

## Decisions

- **winner 口径各自独立**：Aer 侧裸 E winner，真机侧沿用 task9（H_post
  winner）；分歧点是结论的一部分（后选择改变 winner 本身就说明问题），
  不强行统一。替代：统一用裸 E winner——会污染真机侧自洽性，否决。
- **plot_vqe o/s 加 `--os-aer-csv`**：第三线绿色虚线（与黑解析、红真机区分）；
  落盘逻辑、确定性逻辑复用。
- **文件名带 `aer`**：如 `vqe_hw_sym_o_aer_deltam1.png`，落 task8
  figures/os/，与既有 16 个 os 文件并存。

## Risks / Trade-offs

- [winner 分歧误读] → ANALYSIS 列出分歧点清单，明确"同点不同初态"。
- [三线拥挤] → 线型区分（黑实线/绿虚线/红点线），图例写全。

## Migration Plan

不适用。归档后主 specs `viz/vqe-comparison` 追加本需求。

## Open Questions

- 无。

# Proposal

## Why

真机噪声把态踢出 `P=-1` 目标扇区，裸平均里混进了对称性破缺成分。
`doc/postselect/postselect.md` 的 A+B 方案用对称性后选择洗数据：
A 洗 O/S/Q（Z 基留 M=0），B 洗 H（三基各按宇称过滤拼近似）。
task8 的 612 checkpoints（含 X/Y/Z 三基 × 1024）恰好支撑两套方案，
零机时可做；Z_R 无数据，不碰。

## What Changes

- 在 `04_project/variational_param` 下新增 task9（`task9_postselect/`）：
  对 task8 checkpoints 纯后处理，输出结构对标 task8。
- 方案 A：Z 基只留 M=0 字符串，重算 O/S/Q（Q/O/S 获胜初态按 H_post
  的 argmin，保证后选择数据集内部自洽）。
- 方案 B：Z 留 M=0 算 ZZ、X/Y 留偶数个 1 算 XX/YY，拼 H_post
  （诊断量，不当变分上界）。
- 保留率（M=0 占比、三基宇称通过率）单独存诊断 CSV。
- 落盘：E/Q/OS CSV（后选择版）+ min/Q/full/os 四组对照画布；
  figures/ 同样 min/q/full/os 分类。

## Capabilities

### New Capabilities

- `hardware/postselect-ab`: 对真机三基计数做对称性后选择（M=0 洗 O/S/Q，宇称洗 H），输出后选择版 CSV 与对照画布。

### Modified Capabilities

（无）

## Impact

- 新增 `task9_postselect/` 目录（解释器复用 qmeas env）。
- 零真机提交（纯已落盘计数后处理）；读 task8 checkpoints，不写回。
- 无现有代码改动；ZR 不在范围内。

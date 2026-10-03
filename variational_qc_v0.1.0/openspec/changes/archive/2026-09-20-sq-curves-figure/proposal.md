# Proposal

## Why

全套热力图默认只画 `S(π)` 切片，却从未说明为何 π 是正确动量：一张"三相各取一经典点、S(q) 随 q 变化"的三线图能同时回答两个问题——AFM 峰又尖又高（π 是唯一信息位），平庸/SPT 只是 O(1) 宽包（故 S(q) 分不开它俩，这正是需要 string/ZR 的理由）。探索阶段已用存档验证三线形状（平庸恰为 `1-cos q`，SPT 近乎重合，AFM 在 π 处为针状峰 8.0）。

## What Changes

- 从基态存档取三行（平庸 `(s,δ)=(0,0)`、SPT `(1,0)`、AFM 取实测峰值格点 `(≈0.58,3.0)`），在 `q∈[0,2π]` 密采样（约 200 点，OBC 下动量无量子化）下 Fourier 求和得 `S(q)`，纵轴用归一 `S̃(q)=S(q)/8`（与 S̃ 热力图同语言，峰顶 1）。
- 输出一张三线一图 `Sq_curves.png/pdf`（图例区分三相，π 处竖线标记，标题无边界条件字样）；纯秒级后处理，不碰求解与存档。
- `doc/model/operator.md` 不动（用户明确要求）。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `numerics/string-afm-observables`: 新增 `S(q)` 曲线计算 requirement（既有行为不动）。
- `viz/string-afm-heatmaps`: 新增 `S(q)` 三线图 requirement（既有三/四张图不动）。

## Impact

- 新增：一个后处理脚本（读存档三行，输出曲线 CSV 或直出图数据）、一张图；无新增依赖；存档、求解、既有 CSV/图均不动。

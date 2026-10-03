# Spec Delta

## ADDED Requirements

### Requirement: S(q) 曲线计算

系统 SHALL 从基态存档取三行（平庸 `(s,δ)=(0,0)`、SPT `(1,0)`、AFM 取 `S(π)` 实测峰值所在格点），在 `q∈[0,2π]` 密采样（不少于 200 点）下按 `doc/model/operator.md` 的 Fourier 定义计算 `S(q)`（OBC 格点标号约定不变），输出曲线 CSV（三列曲线数据）与取点元数据 `Sq_points.csv`（`curve,s,delta` 三行，图例坐标来源）；计算 SHALL 为纯存档后处理，不得重跑求解。

#### Scenario: 形状符合预期

- **WHEN** 计算三条曲线并取 `q=0, π/2, π` 处的值
- **THEN** 平庸线为 `(0, 1, 2)`（即 `1-cos q`，容差 `1e-8`）、SPT 线近乎重合（峰值 `≈2`，容差 `0.05`）、AFM 线在 π 处为 `≈8` 而其余处接近 `0`（容差 `0.05`）

#### Scenario: 可复算

- **WHEN** 用存档同行独立重算任一 `q` 点
- **THEN** 结果一致（浮点舍入内）；同一存档跑两次逐位一致

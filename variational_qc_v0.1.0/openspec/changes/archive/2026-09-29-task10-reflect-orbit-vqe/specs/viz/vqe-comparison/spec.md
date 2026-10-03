# Spec Delta

## ADDED Requirements

### Requirement: orbit 逐深度画布组

系统 SHALL 对每个深度（`n ∈ {1,2,3}`）、每条 `δ` 切线渲染三个画布：min-energy 三线（解析 `E0`/`E1` + 该深度 `min(VQE-orbit)`）、Q 双线（解析 `Q` + 该深度 `Q_vqe`）、ZR 双线（解析 `tilde_Z_R` + 该深度 `ZR_vqe`），其中 `Q_vqe`/`ZR_vqe` SHALL 由该深度获胜 orbit thetas 经既有派生定义纯后处理得到（不得重跑优化）；各画布横轴 `s∈[0,1]`，纵轴与既有同类画布同语言（能量绝对值、Q `[-1,1]`、ZR `[-1.2,1.2]`），标题保留 orbit 标识、深度、`δ` 取值与方法标识、无边界条件字样，落盘为 PNG（必选）与 PDF（可选同名）于本任务该深度专属 figures 目录（文件名 SHALL 含 orbit 与深度标识，不得与 task3/task4 或其他深度混淆）；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: orbit 效应可判读

- **WHEN** 并排查看同一 `δ` 下 orbit 各深度的 min-energy 画布，并与 task3/4 同深度 uniform 画布对照
- **THEN** 每图线齐全图例可分；orbit 相对 uniform 的能量贴合差与 `Q`/`ZR` 相落点偏移如实呈现（均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

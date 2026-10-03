# Spec Delta

## ADDED Requirements

### Requirement: 能谱画布渲染

系统 SHALL 从 `numerics/spectra-at-fixed-delta` 输出的谱 CSV 渲染能谱画布：每任务一个画布、两个子图（左 `δ=-1`、右 `δ=+1`），横轴 `s∈[0,1]`、纵轴绝对能量，每子图两条线（`E0` 基态、`E1` 第一激发态，图例区分），含轴标签与标题（标题保留任务标识与 `δ` 取值、无边界条件字样），落盘于各任务专属 figures 目录（PNG 必选、PDF 可选同名）；输入缺失或缺 `E0`/`E1` 列时 SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: 隙开合可判读

- **WHEN** 用默认谱 CSV 生成任一任务的能谱画布
- **THEN** 图片非空，两子图各有两条线；task1 画布在简并区两线重合、task2 画布同区两线分离

#### Scenario: 确定性输出

- **WHEN** 同一谱 CSV 运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

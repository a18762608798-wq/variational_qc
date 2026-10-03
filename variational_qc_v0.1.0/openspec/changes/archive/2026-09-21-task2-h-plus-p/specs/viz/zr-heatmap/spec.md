# Spec Delta

## ADDED Requirements

### Requirement: task2 归一化 Z_R 热力图

系统 SHALL 从 task2 的 `tilde_ZR` CSV 渲染归一化 `Z_R` 热力图（与 task1 同渲染约定：横轴 `s∈[0,1]`、纵轴 `δ∈[-3,3]`、发散色标、标题无边界条件字样且保留物理量与链长标识），落盘于 task2 专属 figures 目录（PNG 必选、PDF 可选同名）；输入缺失或缺列时以非零退出码失败且不产生残缺图片。

#### Scenario: 与 task1 可对照

- **WHEN** 用 task2 默认 `100×100` CSV 生成该图
- **THEN** 图片非空且与 task1 对应图逐像素一致（验证通过时）；同一输入运行两次逐像素一致

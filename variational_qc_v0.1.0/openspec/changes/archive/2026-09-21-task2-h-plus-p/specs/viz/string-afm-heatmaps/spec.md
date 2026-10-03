# Spec Delta

## ADDED Requirements

### Requirement: task2 Q 热力图

系统 SHALL 从 task2 的 `Q` CSV 渲染 `Q` 热力图（与 task1 同渲染约定：RdBu 发散色标、中心 `0`、范围 `[-1,1]`、标题无边界条件字样且保留物理量与链长标识），落盘于 task2 专属 figures 目录（PNG 必选、PDF 可选同名）；输入缺失或缺 `Q` 列时以非零退出码失败且不产生残缺图片；不得为 task2 的 `Ostr`/`Spi` 画热力图。

#### Scenario: 与 task1 可对照

- **WHEN** 用 task2 默认 `100×100` CSV 生成该图
- **THEN** 图片非空，平庸侧接近 +1、拓扑侧接近 −1、AFM 区接近 0；验证通过时与 task1 对应图逐像素一致；同一输入运行两次逐像素一致

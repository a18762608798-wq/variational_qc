# viz/zr-heatmap Specification

## Purpose

将归一化拓扑不变量的数值结果转化为可读、可发表的相图热力图：只消费中间数据文件做渲染，为模型相图判读与后续论文/报告插图提供稳定输出。

## Requirements

### Requirement: 纯文件输入渲染

系统 SHALL 仅从 `numerics/zr-ground-state` 输出的 CSV 读取 `(s,delta,tilde_ZR)` 三元组做渲染，不得在绘图代码中重算哈密顿量、基态或 ZR；输入缺失或表头不符时 SHALL 以非零退出码失败并打印可读错误。

#### Scenario: 无 Julia 即能画图

- **WHEN** 在仅有 CSV 而无 Julia 环境的机器上运行绘图入口
- **THEN** 仍能生成图片；若 CSV 缺 `tilde_ZR` 列则报错退出且不产生残缺图片

### Requirement: 热力图内容与输出

系统 SHALL 输出热力图：横轴 `s∈[0,1]`、纵轴 `δ∈[-3,3]`、颜色为 `tilde_ZR` 的发散色标（中心对应 `0`，并标注色棒范围），含轴标签与标题，落盘为 PNG（必选）与 PDF（可选同名）；默认读取默认网格 CSV 即得完整相图。

#### Scenario: 相图可判读

- **WHEN** 用默认 `100×100` CSV 生成热力图
- **THEN** 图片中 `s≈0` 侧与 `s≈1` 侧颜色符号相反（与数值符号一致），色棒标出 `-1/0/+1` 刻度，图片文件非空且尺寸符合文档声明

#### Scenario: 确定性输出

- **WHEN** 同一 CSV 运行绘图两次
- **THEN** 两次输出逐像素一致（除元数据时间戳外字节可比或文档声明容差），输出路径按文档约定（如 `data/figures/tilde_ZR_heatmap.png`）且覆盖前写出原子性不残留半文件

### Requirement: 图像标题不强调边界条件

系统 SHALL NOT 在热力图标题与轴标签中出现 `OBC`/`PBC` 或“开边界/周期边界”字样（后续无周期边界内容，不会产生歧义）；标题仍须保留物理量（`tilde Z_R`）、链长与子系统尺寸标识。

#### Scenario: 标题无边界条件字样

- **WHEN** 查看生成的热力图标题与轴标签
- **THEN** 其中不含边界条件字样，且能读出物理量、链长与子系统信息

### Requirement: task2 归一化 Z_R 热力图

系统 SHALL 从 task2 的 `tilde_ZR` CSV 渲染归一化 `Z_R` 热力图（与 task1 同渲染约定：横轴 `s∈[0,1]`、纵轴 `δ∈[-3,3]`、发散色标、标题无边界条件字样且保留物理量与链长标识），落盘于 task2 专属 figures 目录（PNG 必选、PDF 可选同名）；输入缺失或缺列时以非零退出码失败且不产生残缺图片。

#### Scenario: 与 task1 可对照

- **WHEN** 用 task2 默认 `100×100` CSV 生成该图
- **THEN** 图片非空且与 task1 对应图逐像素一致（验证通过时）；同一输入运行两次逐像素一致

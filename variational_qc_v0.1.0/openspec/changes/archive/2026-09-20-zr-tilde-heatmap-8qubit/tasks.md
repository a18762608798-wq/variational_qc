# Tasks

## 1. 环境与仓库骨架

- [x] 1.1 按 env-python skill 创建 Python 环境（优先 julia-condapkg 方式）并锁定 numpy+matplotlib，验证 `python -c "import numpy, matplotlib; print(numpy.__version__)"` 成功
- [x] 1.2 创建 Julia 环境（Project.toml 锁定 QuantumToolbox.jl）并验证 `julia --project=. -e 'using QuantumToolbox'` 成功
- [x] 1.3 创建精简骨架 `src/numerics,src/viz,src/shared/io,src/shared/config,data/interim,data/figures`（仅本次真实边界，不预设未来目录）并验证 `ls` 目录齐全且仅含一个 `shared/`

## 2. Julia 数值基线（对应 numerics/zr-ground-state）

- [x] 2.1 实现 OBC `H(s,δ)` 构造（键表见 spec，`L=8` 无 `(7,0)` 键），验证 `s=0/1` 端点键数正确且哈密顿量厄米
- [x] 2.2 实现单点基态求解（归一化，简并标记 `is_degenerate`），验证任一点模长为 1、能量为最小本征值（容差 `1e-8`）
- [x] 2.3 实现 `tilde Z_R` 计算链（`ρ_I/R_I/Z_R/纯度/比值`，`I={2,3,4,5}`），验证 `s=0` 端为正、`s=1` 端为负且输出在 `[-1.2,1.2]` 内
- [x] 2.4 实现 `11×11` 冒烟扫描并输出 CSV，验证行数 `121` 且 `s∈[0,1]、δ∈[-3,3]` 端点齐全
- [x] 2.5 运行默认 `100×100` 全网格输出 `data/interim/tilde_ZR_L8_OBC.csv`（`δ` 外层、`s` 内层），验证行数 `10000` 且 Python 端无需 Julia 即可读取

## 3. Python 热力图（对应 viz/zr-heatmap）

- [x] 3.1 实现纯 CSV 输入的绘图入口（缺列/缺文件时非零退出并打印可读错误，绝不重算物理），验证删除 `tilde_ZR` 列后报错退出且无残缺图片
- [x] 3.2 实现热力图渲染（横轴 `s`、纵轴 `δ`、发散色标中心 `0`、色棒含 `-1/0/+1`、轴标签标题），验证 `data/figures/tilde_ZR_heatmap.png` 非空且两侧颜色符号与 CSV 一致
- [x] 3.3 保证确定性输出（同 CSV 两次运行逐像素一致，原子写出），验证两次运行图片哈希一致且无半文件残留
- [x] 3.4 图像标题不含边界条件字样（`OBC`/`PBC`/开边界/周期边界），验证标题含 `tilde Z_R`、链长与子系统信息且无边界条件字样

## 4. 集成验收

- [x] 4.1 端到端复跑（Julia 全网格→Python 出图）并记录端点 `tilde Z_R` 值与图片路径，验证产物与 specs 场景一一对应

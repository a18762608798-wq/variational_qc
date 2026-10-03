# Tasks

## 1. solver 透出第一激发态

- [x] 1.1 `solve_ground_state` 返回追加 `excited`（第一激发态能量），验证旧调用（task1/task2 求解链）行为不变且 `excited - energy == gap`

## 2. 谱扫描与存档

- [x] 2.1 实现谱扫描脚本（`δ ∈ {-1,+1}` × `s` 201 点，`build_H`/`build_Hp` 可选），验证输出 `spectra_L8_OBC.csv` 共 `402` 行、表头 `s,delta,E0,E1`、逐行 `E1 ≥ E0`
- [x] 2.2 运行 task1 与 task2 谱扫描，验证两 CSV 各 `402` 行、两次运行逐位一致；核对 task2 简并区隙被撑开、非简并区 `E0` 差 −1（容差 `1e-8`，`E1` 如实记录）

## 3. 能谱图与收尾

- [x] 3.1 实现 `plot_spectra.py`（一画布两子图、共享 y 轴、原子写出），验证 task1 画布简并区两线重合、task2 同区两线分离
- [x] 3.2 生成两任务能谱画布（PNG 必选、PDF 可选），验证同一输入两次运行逐像素一致、标题无边界条件字样
- [x] 3.3 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

# Tasks

## 1. 分量输出与画布

- [x] 1.1 `derive_hw.py` 加 O/S 四列输出（新 CSV，不动旧表头），验证行数 102、行序与 task3 一致、Q 可由分量复算（容差 1e-9）
- [x] 1.2 `plot_vqe.py` 加 `o`/`s` 模式，渲染 8 张对照图（PNG+PDF），验证线齐全、标题无边界条件字样、两次运行逐像素一致

## 2. 整理与验收

- [x] 2.1 figures/ 下建 min/q/full/os 子目录并搬入现有图片，验证文件数一致、无散文件
- [x] 2.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

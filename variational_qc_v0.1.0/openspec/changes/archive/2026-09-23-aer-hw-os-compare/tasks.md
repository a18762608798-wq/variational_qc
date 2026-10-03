# Tasks

## 1. Aer 导出与三线图

- [x] 1.1 由 task3/task5 thetas 精确导出 Aer O/S CSV（winner 口径裸 E argmin，102 行），验证 Q 可由分量复算且与 task3/5 Q CSV 一致（容差 1e-9)
- [x] 1.2 `plot_vqe.py` o/s 模式加 Aer 第三线，渲染 8 张三线图（PNG+PDF），验证三线齐全、标题无边界条件字样、两次运行逐像素一致

## 2. 沉淀与验收

- [x] 2.1 写三线对比结论进 `task8_hardware_vqe/ANALYSIS.md`（表达缺口 vs 硬件 penalty 分段、winner 分歧点清单）——文件不存在则新建
- [x] 2.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

# Tasks

## 1. 后选择合成

- [x] 1.1 建 `task9_postselect/` 目录，写过滤合成脚本（A：Z 留 M=0；B：三基宇称过滤拼 H_post），输出 E/Q/OS/retention 四套 CSV，验证行数行序与 task8 一致、空集记 NaN 不中断
- [x] 1.2 渲染 min/Q/full/os 四组对照画布（PNG+PDF，H_post 标题声明诊断量），验证线齐全、两次运行逐像素一致

## 2. 沉淀与验收

- [x] 2.1 写 `task9_postselect/ANALYSIS.md`（A/B 对比结论、保留率塌点）
- [x] 2.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

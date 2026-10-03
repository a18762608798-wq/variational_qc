# Tasks

## 1. 项目结构重组与 task1 搬迁

- [x] 1.1 建 `shared/`、`task1_baseline/`、`task2_hplusp/` 骨架并 `git mv` 旧 `src/`、`data/` 内容，验证 `git status` 只显示重命名、无内容改动
- [x] 1.2 拆分 grid 配置为每任务一份（task1 路径指向新位置），验证 task1 烟测（11×11 求解+derive+画图）可跑且产物落新目录
- [x] 1.3 抽取复用件进 `shared/`（H 构造器、io、CSV schema、画图 helpers），验证 task1 全链仍可用 shared 件跑通烟测

## 2. H+P 求解与 task2 存档

- [x] 2.1 实现 `build_P`（`Z_tot^2 − ∏X`）与 `build_Hp`（λ=1 硬编码），验证 `[H,P]` 交换子范数在浮点舍入内且 `(M=0,+1)` 扇区本征值为 `−1`
- [x] 2.2 task2 烟测求解（11×11）并输出存档，验证五个 keys 齐全、`psi` 形状 `(121, 256)`、行模长为 1
- [x] 2.3 task2 全网格求解（100×100）并输出存档，验证行数 `10000`、网格端点覆盖 `[0,1]`/`[-3,3]`，同行 energies 比 task1 低 `1`（容差 `1e-8`，偏离行记入异常清单）

## 3. task2 derive 与一致性验证

- [x] 3.1 参数化 derive 脚本（输入/输出路径可配）并跑出 task2 四个 CSV，验证各 `10000` 行、行序与 task2 存档一致
- [x] 3.2 实现 `compare_task1_task2.py`（四个对比列容差 `1e-8`、energies 差 −1 预期、`is_degenerate` 翻转单独列出），验证在 task1 自对比上输出通过、差异清单为空
- [x] 3.3 运行 task1/task2 对比，验证输出 pass/fail 结论与差异行清单（`s,delta,列,两值`）；通过则对称性预期成立，不通过则差异如实记录为结论

## 4. task2 两图与收尾

- [x] 4.1 参数化画图入口并生成 task2 归一化 `Z_R` 热力图（PNG 必选、PDF 可选），验证图片非空、标题无边界条件字样、同一输入两次运行逐像素一致
- [x] 4.2 生成 task2 `Q` 热力图（同上约定），验证平庸侧 +1、拓扑侧 −1、AFM 区 0；确认未产出 `Ostr`/`Spi` 热力图与 `S(q)` 产物
- [x] 4.3 跑 `openspec validate --specs` 全通过，同步四个 delta 进主 specs，确认可归档

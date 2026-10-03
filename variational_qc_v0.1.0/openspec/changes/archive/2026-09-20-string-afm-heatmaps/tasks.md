# Tasks

## 1. 求解与存档（对应 numerics/zr-ground-state 新增部分）

- [x] 1.1 添加 NPZ.jl 依赖并实现 `solve.jl`（网格循环+对角化，只写 `psi_archive.npz`），验证 `julia --project=. -e 'using NPZ'` 成功且冒烟网格（`11×11`）存档 keys 齐全
- [x] 1.2 验证存档契约：用 numpy（无 Julia）读回，断言形状 `(121, 256)`、抽查行模长为 1、`s/delta` 端点齐全，且存档第 `k` 行重算值与行序一致
- [x] 1.3 `grid.toml` 加存档路径项，`psi_archive.npz` 加入 gitignore，验证 `git status` 不再列出存档

## 2. ZR 迁移（对应 numerics/zr-ground-state 修改部分）

- [x] 2.1 实现 `derive_zr.jl`（只读存档，复用既有 ZR 公式链写 CSV），验证冒烟存档派生 CSV 与行序一致
- [x] 2.2 全网格派生并与历史 `tilde_ZR_L8_OBC.csv` diff，验证逐行一致（容差 `1e-8`），通过后删除旧 `scan.jl` 直算链

## 3. string 与 AFM 派生（对应 numerics/string-afm-observables）

- [x] 3.1 实现 string operator 模块并验证公式可审计（追溯到存档行与算符构造）、同存档两次运行逐位一致、绕过存档直算交叉一致（容差 `1e-8`）
- [x] 3.2 实现 AFM 结构因子模块并验证非负性、同存档两次逐位一致、直算交叉一致（容差 `1e-8`）
- [x] 3.3 实现 `derive_string.jl`/`derive_afm.jl` 输出双 CSV，验证默认网格各 `10000` 行且第 `k` 行与存档第 `k` 行 `(s,delta)` 一致

## 4. 热力图（对应 viz/string-afm-heatmaps）

- [x] 4.1 参数化 `plot_heatmap.py`（值列与标题参数）并输出两张 PNG+PDF，验证非空且 string 图两侧显著不同、`S(π)` 图非负
- [x] 4.2 验证两图标题无边界条件字样且保留物理量/链长/子系统信息，两次运行逐像素一致，缺列报错无残图

## 5. 集成验收

- [x] 5.1 端到端复跑（求解→三派生→三图）并记录三图路径与端点值，验证产物与 specs 场景一一对应

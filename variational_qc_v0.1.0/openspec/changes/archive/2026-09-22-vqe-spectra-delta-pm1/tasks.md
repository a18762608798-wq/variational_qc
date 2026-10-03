# Tasks

## 1. 环境与骨架

- [x] 1.1 `CondaPkg.toml` 加 `qiskit`、`qiskit-aer` 并重建 pixi env，验证项目 python 可 `import qiskit, qiskit_aer` 且 `AerSimulator(method='statevector')` 可用
- [x] 1.2 建 `task3_vqe/` 骨架（脚本目录、`data/{interim,figures}`、网格与优化配置），验证目录结构与路径配置就绪

## 2. 拟态与 pilot

- [x] 2.1 实现三初态制备 + 单层拟态（含子层顺序配对）与裸 `H` 期望函数，验证拟态 `P` 期望为 `−1`（浮点舍入内）且三初态在其标定点（`doc/qc/initial_state.md`）与解析基态保真度符合文档声明
- [x] 2.2 实现两步优化（`differential_evolution` + COBYLA polish，seed 确定性派生），验证同 seed 两次逐位一致
- [x] 2.3 跑 pilot（3~5 个 `s` 点 × 三初态），输出预算-最优值收敛与多 seed 极差结论，验证 polish 不差于全局解且极差收敛，据此锁定全量预算

## 3. 全量扫描与两图收尾

- [x] 3.1 并行跑全量扫描（2 `δ` × 51 `s` × 3 初态），验证输出 CSV 共 `102` 行、表头 `s,delta,E_triv,E_topo,E_afm`，且逐行满足变分上界 `E_init ≥ E0 − 1e-6`
- [x] 3.2 生成两张五线对照画布（PNG 必选、PDF 可选），验证 5 线齐全图例可分、同一输入两次运行逐像素一致、标题无边界条件字样
- [x] 3.3 跑 `openspec validate --specs` 全通过，同步两个 delta 进主 specs，确认可归档

## 4. min-VQE 三线图

- [x] 4.1 生成两张三线对照画布（`min(VQE)` + `E0` + `E1`，PNG 必选、PDF 可选，文件名与五线图区分），验证 3 线齐全图例可分、`min` 线包络性（逐点 ≤ 任一初态线且 ≥ `E0 − 1e-6`）、同一输入两次运行逐像素一致、标题无边界条件字样
- [x] 4.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

## 5. VQE-Q 双线图

- [x] 5.1 实现 Q 算子（LSB 序 Z-对角）与 VQE-Q 派生脚本并输出 VQE-Q CSV（`s,delta,Q_vqe`，102 行），先过 Julia 存档交叉验证（容差 `1e-8`），再验证两次运行逐位一致
- [x] 5.2 生成两张双线对照画布（`Q_vqe` + 解析 `Q`，PNG 必选、PDF 可选，文件名与现有四图区分），验证 2 线齐全图例可分、同一输入两次运行逐像素一致、标题无边界条件字样
- [x] 5.3 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

## 6. VQE-ZR 双线图

- [x] 6.1 实现 ZR 算子（约化密度矩阵路线）与 VQE-ZR 派生脚本并输出 VQE-ZR CSV（`s,delta,ZR_vqe`，102 行），先过 Julia 存档交叉验证（容差 `1e-8`），再验证两次运行逐位一致
- [x] 6.2 生成两张双线对照画布（`ZR_vqe` + 解析 `tilde_Z_R`，PNG 必选、PDF 可选，文件名与现有六图区分），验证 2 线齐全图例可分、同一输入两次运行逐像素一致、标题无边界条件字样
- [x] 6.3 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

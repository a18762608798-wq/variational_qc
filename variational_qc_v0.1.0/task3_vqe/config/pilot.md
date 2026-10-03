# pilot 结论（vqe-spectra-delta-pm1 task 2.3）

pilot 范围：`δ=+1` 上 `s ∈ {0.0, 0.5, 0.98}` × 三初态 × 3 seed × 两档预算
（light: de_maxiter=30/popsize=10/cobyla=300；base: 50/10/500），共 54 runs。
产物：`task3_vqe/data/interim/pilot.csv`。

## 结论

1. **预算取 light 档**：两档预算 polish 后最小值在所有 9 个点-初态上 6 位小数一致，
   base 档无可测增益，只更慢。全量用 light。
2. **必须 3 seed 取最优**：坏 basin 靠预算救不回来（s=0.5 triv、s=0.98 triv 各 1/3 seed
   系统性偏高 0.03~0.07，light/base 同陷）；取最优后各点极差归零。单 seed 全量约 1/4
   坏点率，不可接受。
3. **polish 恒有效**：全局解→polish 增益 1e-4~1e-1，无一恶化（容差内）。
4. **变分上界全成立**：全部 54 runs 满足 `fun ≥ E0 − 1e-6`。
5. **物理预览**：s=0 处 triv 贴 E0 到 3e-8；s=0.98 处 topo 距 E0 2e-3；
   s=0.5 过渡区三初态最优仍高 E0 0.156（单层表达瓶颈，记为结论非失败）。
6. **确定性边界**：同 seed 结果随 BLAS 线程数末位分叉（实测一例轨迹分叉改换 basin）。
   全量脚本必须钉死 `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`，
   且"逐位一致"断言只在同线程环境下有意义。

## 锁定全量配置

- budget = light（de_maxiter=30, de_popsize=10, cobyla_maxiter=300）
- seeds = 3（`derive_seed(base, s, delta, init, restart∈{0,1,2})`），逐点取最优
- workers = 8，单线程 BLAS；预计 918 runs × ~20s / 8 ≈ 40 min

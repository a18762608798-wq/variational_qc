# pilot 结论（vqe-nosym-inits task 2.2）

pilot 范围：`δ=+1` 上 `s ∈ {0.0, 0.5, 0.98}` × 三 nosym 初态 × 微扰 `{0.2, 0.4, 0.6}`
× 2 restart，depth1 nosym 最优直跳 depth5，共 54 链。
产物：`task5_vqe_nosym/config/pilot.csv`（+ ckpt）。

## 结论

1. **直跳有效**：除已收敛点（s=0 triv、s=0.98 topo 零增益，预期内）外全线有增益；
   s=0.98 triv −5.88→−8.49，s=0.5 triv −8.70→−9.42，s=0 topo −5.73→−7.39。
2. **微扰取 0.4**：三档互有胜负但差值小，0.4 居中且从不是最差。全量锁定 0.4。
3. **耗时**：每链中位 48s；全量 306 链 /8 workers ≈ 30min。
4. **restart 保留 3 组**：逐点取最优（沿用 task3/4 结论）。

## 锁定全量配置

- perturb_scale = 0.4，n_restarts = 3，cobyla_maxiter = 500，workers = 8
- 单线程 BLAS；增量 checkpoint，abort-safe

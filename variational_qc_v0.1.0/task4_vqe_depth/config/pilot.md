# pilot 结论（vqe-depth-scaling task 2.2）

pilot 范围：`δ=+1` 上 `s ∈ {0.0, 0.5, 0.98}` × 三初态 × 微扰 `{0.1, 0.3}` × 2 restart，
每条链 L1→L2→L3→L4→L5 逐层 warm-start（task3 thetas 出发），共 36 链。
产物：`task4_vqe_depth/config/pilot.csv`（+ ckpt）。

## 结论

1. **深度有效**：单层最差的点增益最大（s=0.5 triv −8.70→−9.40、topo −7.15→−9.41；
   s=0.98 triv −5.88→−9.49；s=0 topo −5.73→−11.87）；已收敛点零增益（预期内）。
   s=0.5 处 afm L5 距 E0 仅 0.01（−9.734 vs −9.743），过渡区缺口基本闭合。
2. **微扰取 0.3**：0.3 在几乎所有点-初态上 ≥ 0.1，无一反例。全量锁定 0.3。
3. **单调钳位成立**：深层以下不差于垫底（零微扰即浅层最优），退化场景未触发。
4. **耗时**：每链（4 次 warm-start）77~145s；全量每深度 306 链 /8 workers ≈ 1h，
   四深度约 4h（串行，链式依赖）。
5. **restart 保留 3 组**：沿用 task3 结论（坏 basin 需换 seed），此处 pilot 用 2 组仅为定尺度。

## 锁定全量配置

- depths = [2, 3, 4, 5]（pilot 通过，不砍集合）
- perturb_scale = 0.3，n_restarts = 3，cobyla_maxiter = 500，workers = 8
- 单线程 BLAS（同 task3）；增量 checkpoint，abort-safe

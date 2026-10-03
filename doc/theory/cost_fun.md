# cost_fun

目标相点 $(s^{*},\delta^{*})$ 处，从三个相起点各做一路优化，取综合最小。记初态指标 $a\in\{{\rm triv},{\rm topo},{\rm AFM}\}$，每路代价函数为 $H$ 在该路拟设态下的期望：

$$
C_{a}(\theta)=\langle\psi_{a}(\theta)|H(s^{*},\delta^{*})|\psi_{a}(\theta)\rangle
$$

* $|\psi_{a}(\theta)\rangle = U(\theta)\,|\psi_{\mathrm{init},a}\rangle$，即 [orbit 拟设](./ansatz.md)电路作用在[初态](./psi0.md) $a$ 上的态；
* 上报的最优值为三路分别优化后再取最小：

$$
C^{*}(s^{*},\delta^{*})=\min_{a}\min_{\theta}C_{a}(\theta)
$$

* 每路内可用多种子 restart，同样取最小.

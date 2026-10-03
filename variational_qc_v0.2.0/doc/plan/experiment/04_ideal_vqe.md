# 04 ideal variational preparation

本实验提供 `实验结果展示` 所需理想参数电路数值.

本数值实验的系统尺度 $L = 8$，$H$ 参数取 $s \in [0, 1]$，$\delta = 0, 0.85$，以 julia `Yao.jl` 态矢量模拟做理想优化（不计噪声、不计 shots）.

$$
|\psi_{\rm init}\rangle \xrightarrow{U_{p}(\theta)} |\psi(\theta^{*})\rangle
$$

## 优化设置

* ansatz 用 theory/ansatz.md 的 orbit 拟设，cost 用 theory/cost_fun.md 的 energy cost；
* $\delta=0,0.85$ 两条线，$s$ 取 03 定死的 49 个点，分别做 $p=1,\dots,5$；
* $\delta=0$ 时每轨道 $\theta_{1}=\theta_{2}$，按减半后的参数优化；$\delta=0.85$ 用正常全参数；
* 优化参数空间限制为所有参数 $\theta\in[-\pi,\pi]$；
* 初态三路各做一路优化（平庸 / 拓扑 / AFM），子层顺序按 ansatz.md 的 $F$ 规则，最终取三路最小（见 cost_fun.md）；
* 本步只在逻辑 $L=8$ 电路上优化 $\theta^{*}$，不做硬件映射；拓扑初态的 $(1,8)$ 对在模拟中直接用长程门.

## GHZ 初态冗余参数（AFM 初态分支，与扫描 $\delta$ 无关；本轮即 $\delta=0.85$ 线）

AFM 初态取 psi0.md 的 GHZ 猫态 $|\psi_{\rm AFM}\rangle$，两支都是 $Z$ 本征态且同键 $ZZ$ 本征值相同，首层先作用的偶键子层上独立的 $ZZ$ 转角只给整体相位。因此 AFM 初态分支删掉首层首个偶子层的两个独立 $ZZ$ orbit 参数（$L=8$ 时即 $e_{{\rm out},2}$、$e_{c,2}$），固定为 0 不优化。

$\delta=0$ 时已有 $\theta_{1}=\theta_{2}\equiv\theta$，不存在可单独删掉的 $\theta_{2}$，共享参数中的 $XX+YY$ 部分仍改变状态，故不额外删参数。

## warm start 参数起点

* $p=1$：从零开始全局优化（differential_evolution）+ COBYLA polish，$n_{\rm seeds}=3$，seed 按 $(s,\delta,{\rm init},{\rm restart})$ 确定性派生；
* $p\ge2$：以上一深度同 $(s,\delta,{\rm init})$ 最优 $\theta^{*}$ 为垫底，新增一层参数以均匀微扰 $U(-0.3,0.3)$（rad）初始化，$\times n_{\rm restarts}$ 后 COBYLA polish，劣于垫底则钳位保留垫底；
* GHZ 冻结参数与 $\delta=0$ 减半规则与上述起点规则叠加：冻结位恒为 0，减半位只优化共享参数。

## 子实验结果呈现

* 主文图：exact 与 variational 的 $E$、$S(\pi)$、$O_{\rm str}$ 随 $s$ 对比曲线（$p=1,\dots,5$ 同图），回答 ansatz 能否把态制备出来。
* 本实验数据完备后即画图验收，不等待其他实验。

# operator

## string operator

$$
O_{\rm str}(d)=(Z_{0}+Z_{1})\left[\prod_{l=1}^{d-1}(-Z_{2l}Z_{2l+1})\right](Z_{2d}+Z_{2d+1})
$$

* $d$ 为 unitcell 距离；
* 起点固定 $k=0$，即格点 $0,1$；
* $1/4$ 归一已略去。

特殊值设置（OBC）：

$$
O_{\rm str}=\langle O_{\rm str}(d=L/2-1)\rangle
$$

**注意测量时需要一次shot估计 $O_{\rm str}$ 整体**

归一化显示版（作图用）：

$$
\tilde O_{\rm str}=-O_{\rm str}
$$

* 取反不取绝对值：拓扑端 $-1\to+1$，平庸端 $0$ 不变；线性无损，符号链条可审计；
* 注意这不是文献的 $1/4$ 归一：本变式本就略去 $1/4$，故 $\tilde O_{\rm str}$ 等于文献值 $\times(-4)$；
* SPT 端的 $+1$ 是该分支的饱和值，不是量子化普适数。

## AFM 结构因子

$$
S(q)=\frac{1}{L}\sum_{i=0}^{L-1}\sum_{j=0}^{L-1}e^{iq(i-j)}\langle Z_{i}Z_{j}\rangle
$$

$q=\pi$ 时：

$$
S(\pi)=\frac{1}{L}\sum_{i=0}^{L-1}\sum_{j=0}^{L-1}(-1)^{i-j}\langle Z_{i}Z_{j}\rangle
$$

* $i,j$ 为格点标号，$L$ 为格点数，$1/4$ 归一已略去；
* 反铁磁判据看 $q=\pi$ 处有峰：Néel 相 $S(\pi)\propto L$，dimer / SPT 相 $S(\pi)$ 仅 $O(1)$。

**不同于string operator, 这个力学量的测量确实是多个期望的线性组合函数,
当然实际上和直接用shot估计整体效果相同.**

归一化显示版（作图用）：

$$
\tilde S(\pi)=S(\pi)/8
$$

* Néel 饱和 $8\to1$，其余等比压缩，全场非负；
* 换算：本变式略去 $1/4$，故 $S(\pi)$ 为 $S^{z}$ 原式值的 $4$ 倍；$\tilde S$ 等于原式值 $\times(1/2)$，$L=8$ 下 Néel 原式值 $L/4=2$ 对应 $\tilde S=1$；
* 下限 $0$ 只有铁磁态才取到，基态中不出现。

## ZR-like 组合显示量

用归一化 string 与归一化结构因子的线性组合，拼出与 ZR 同语言的相图：平庸相 $+1$，拓扑相 $-1$，反铁磁相 $0$。

$$
Q=(1-2\tilde O_{\rm str})-\frac{4}{3}\left(\tilde S(\pi)-\frac{1}{4}\right)
$$

* 第一项为 string 符号项：平庸 $+1$、SPT $-1$；
* 第二项为 AFM 惩罚项：dimer / SPT 区 $\tilde S\approx1/4$ 时为零，AFM 区 $\tilde S\to1$ 时为 $1$，恰抵消第一项；
* 系数唯一性：线性形式 $Q=a\tilde O+b\tilde S+c$ 有三个自由参数，三相锚点（平庸 $(0,1/4)\to+1$、SPT $(1,1/4)\to-1$、AFM $(0,1)\to0$）联立得唯一解 $a=-2$、$b=-4/3$、$c=4/3$；
* $1/4$ 基线只在退耦合 dimer 点严格成立（单态乘积给出 $S(\pi)=2$），其余区域为近似；平面插值只在锚点处精确；
* 显示构造，不可直接测量：$Q$ 是期望值的线性组合，只能经典后处理作图；硬件可测量不变量仍为 $Z_{\mathcal R}$。

## ZR

$$
Z_{\mathcal R}={\rm Tr}(\rho_{I}{\mathcal R}_{I})
$$

$$
\tilde Z_{\mathcal R}=Z_{\mathcal R}/\sqrt{[{\rm Tr}(\rho_{I_{1}}^{2})+{\rm Tr}(\rho_{I_{2}}^{2})]/2}
$$

* $I=I_{1}\cup I_{2}$ 取中间 $2n$ 比特，$I_{1},I_{2}$ 为左右连续块，各 $n$ 比特；
* ${\mathcal R}_{I}$ 为中央键镜像交换；
* 判据：平庸为 $+1$，拓扑 Haldane 为 $-1$，反铁磁为 $0$。

特殊值设置（OBC，$L$ 为 4 的倍数）：

* $L=8$ 时 $I=\{2,3,4,5\}$，$I_{1}=\{2,3\}$，$I_{2}=\{4,5\}$，反射中心在 $3$-$4$ 键；

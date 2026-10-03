# initial state

## think of symmetry

条件：$H'$ 基态（用 $H'$ 而非 $H$ 以区分简并）+ 易在电路上制备。$|s\rangle=(|01\rangle-|10\rangle)/\sqrt{2}$，格点 $0$-indexed。

### 平庸 $s=0,\delta=-3$：intra 单态乘积

$$
|\psi_{\rm triv}\rangle=\bigotimes_{(0,1),(2,3),(4,5),(6,7)}|s\rangle
$$

* 与 $H'$ 基态保真度 $1$；每对局域 $H+{\rm CNOT}+Z$ 制备。

### 拓扑 $s=1,\delta=-3$：bulk 单态 + 首尾单态

$$
|\psi_{\rm topo}\rangle=|s\rangle_{0,7}\bigotimes_{(1,2),(3,4),(5,6)}|s\rangle
$$

* 裸 $H$ 四重简并，$H'$ 打开 gap 并选出 $P=-1$ 分支，与上式保真度 $1$；
* 中间三对局域制备，$(0,7)$ 对需长程 ${\rm CNOT}$ 或 SWAP 链。

### 反铁磁 $s\approx 0.5,\delta=3$：Neel GHZ

> 理论上不是必须 s=0.5，相内两边都可以；实际取中间只是为了效果最好.

$$
|\psi_{\rm AFM}\rangle=(|01010101\rangle+|10101010\rangle)/\sqrt{2}
$$

* $s=0.5,\delta=3$ 处与 $H'$ 基态保真度 $\approx 1$；注意 $s=0,1$ 处即使 $\delta=3$ 仍是单态乘积，不是反铁磁；
* 制备：奇数位 $X$ + $H$ + 链式 ${\rm CNOT}$，深度 $O(L)$。

## 不考虑对称性（真机简化版）

> 目的：去掉长程/深层制备，深度最小；代价：初态不在 $P=-1$ 扇区。

### 平庸：保持不变

$|\psi_{\rm triv}^{\rm nosym}\rangle=|\psi_{\rm triv}\rangle$，intra 单态乘积本来就是对称的（$P=-1$），无需简化。

### 拓扑：取消 $(0,7)$ link，$0,7$ 空着

$$
|\psi_{\rm topo}^{\rm nosym}\rangle=|00\rangle_{0,7}\bigotimes_{(1,2),(3,4),(5,6)}|s\rangle
$$

* 制备：只需中间三对局域 $H+{\rm CNOT}+Z$，$0,7$ 无门（保持 $|0\rangle$）；省掉长程 ${\rm CNOT}$/SWAP 链；
* 相深处唯一实质影响就是拓扑相的 $S$ 值（$2.0\to1.5$），$O$/$Z_{\mathcal R}$ 分子与反铁磁的 $S$ 全不动；无妨：拓扑区分只用 $O$ 替代需多次测量的 $Z_{\mathcal R}$，具体数值不重要。

### 反铁磁：只取 GHZ 一支

$$
|\psi_{\rm AFM}^{\rm nosym}\rangle=|01010101\rangle
$$

（比特串按格点 $0\to7$，偶位 $0$ 奇位 $1$。）

* 制备：奇数位 $X$，无 $H$、无链式 ${\rm CNOT}$，深度 $O(1)$；

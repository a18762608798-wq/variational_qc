# psi0

格点编号 $1,\dots,L$. $|s\rangle=(|01\rangle-|10\rangle)/\sqrt{2}$ 为两比特单态。

本文 $L=4k$ 使用的三个参考态都在 [$P=-2$](./H.md) 扇区。

## 平庸 $s=0$：奇键单态乘积

$$
|\psi_{\rm triv}\rangle=\bigotimes_{j=1}^{L/2}|s\rangle_{2j-1,2j}
$$

## 拓扑 $s=1$：bulk 单态 + 首尾单态

$$
|\psi_{\rm topo}\rangle=|s\rangle_{1,L}\bigotimes_{j=1}^{L/2-1}|s\rangle_{2j,2j+1}
$$

## 反铁磁 $\delta$ 大：GHZ

$$
|\psi_{\rm AFM}\rangle=(|0101\cdots\rangle+|1010\cdots\rangle)/\sqrt{2}
$$

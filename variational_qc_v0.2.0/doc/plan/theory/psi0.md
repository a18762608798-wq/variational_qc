# psi0

格点编号 $1,\dots,L$. $|s\rangle=(|01\rangle-|10\rangle)/\sqrt{2}$ 为两比特单态。

对称性算符 $P=Z_{\rm tot}^{2}-\prod_{m=1}^{L}X_{m}-R$，其中 $Z_{\rm tot}=\sum_{m=1}^{L}Z_{m}$，$R$ 为全链反射 $m\leftrightarrow L+1-m$。本文 $L=4k$ 使用的三个参考态都有 $R=+1$，最低本征值 $-2$ 当且仅当 $(Z_{\rm tot}=0,+1,+1)$，三个参考态都在 $P=-2$ 扇区。

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

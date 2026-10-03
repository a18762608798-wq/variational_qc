# AHC 哈密顿量

$$
H(s,\delta)=\sum_{i=0}^{d}\left[(1-s)h_{2i,2i+1}(\delta)+sh_{2i+1,2(i+1)}(\delta)\right]
$$

$$
\begin{cases}
d = L/2-1 \\
h_{k,l}(\delta)=e^{-\delta}(X_{k}X_{l}+Y_{k}Y_{l})+e^{+\delta}Z_{k}Z_{l}
\end{cases}
$$

* $L$ 取 4 的倍数，$k=0,\cdots,L-1$，周期边界即 $L\equiv 0$；
* $2i$ 和 $2i+1$ 组成 unitcell $i$；
* $s\in[0,1]$，$1-s=J^{\prime}$，$s=J$；$s=0$ 为平庸 dimer 端，$s=1$ 为 SPT 端；
* $\delta\in[-3,3]$，等效 $\Delta=e^{2\delta}$，$\delta=0$ 回到各向同性点。

## H' = H + P（打开简并用）

$$
P=Z_{\rm tot}^{2}-\prod_{i=0}^{L-1}X_{i}
$$

$$
H'(s,\delta)=H(s,\delta)+\lambda P
$$

$$
Z_{\rm tot}=\sum_{i=0}^{L-1}Z_{i}
$$

* $\lambda=1$ 固定，不做扫描轴；
* $[H,P]=0$，故本征态不变，只做本征值整体移动；基态落在 $P=-1$ 扇区时 $E'=E-1$；
* $P$ 最低本征值 $-1$ 当且仅当 $(M=0,+1)$，$|M|=2$ 扇区本征值为 $3$ 或 $5$，即把对称扇区压低、其余扇区罚掉，在简并处选出确定的一支；
* $H'$ 与 $H$ 键表相同；
* 详细对称性分析见 [symmetry](symmetry.md) 与 [ref/symmetry](ref/symmetry.md)。

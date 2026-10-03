# operator origin

## string operator

### 文献原文

来源：Sun, Shirakawa, Yunoki, PRB 108, 075127 (2023), Sec.III Eq.(3).

文献以 unitcell 总自旋定义：

$$
O_{\rm str}(d)=\mathcal{S}^{z}_{k}\left(\prod_{l=k+1}^{k+d-1}\exp(i\pi\mathcal{S}^{z}_{l})\right)\mathcal{S}^{z}_{k+d}
$$

$$
\mathcal{S}^{z}_{k}=S^{z}_{2k}+S^{z}_{2k+1}
$$

### 到变式的改写

单自旋 $S^{z}_{j}=Z_{j}/2$，故 $\mathcal{S}^{z}_{k}=(Z_{2k}+Z_{2k+1})/2$。

指数项 $e^{i\pi\mathcal{S}^{z}_{l}}=e^{i\pi(Z_{2l}+Z_{2l+1})/2}=(iZ_{2l})(iZ_{2l+1})=-Z_{2l}Z_{2l+1}$。

代回并略去 $1/4$ 归一，固定起点 $k=0$，即得变式，见 [operator](../operator.md)。

## AFM 结构因子（角动量原版形式）

$$
S(q)=\frac{1}{L}\sum_{i=0}^{L-1}\sum_{j=0}^{L-1}e^{iq(i-j)}\langle S^{z}_{i}S^{z}_{j}\rangle
$$

* $i,j$ 为格点标号，$L$ 为格点数；
* 反铁磁 Néel 序对应 $q=\pi$ 处有峰，变式见 [operator](../operator.md)。

## ZR（文献原文）

来源：Elben 等，Sci. Adv. 2020，Eq.(2)，partial reflection 不变量。

$$
Z_{\mathcal R}={\rm Tr}(\rho_{I}{\mathcal R}_{I})
$$

$$
\tilde Z_{\mathcal R}=Z_{\mathcal R}/\sqrt{[{\rm Tr}(\rho_{I_{1}}^{2})+{\rm Tr}(\rho_{I_{2}}^{2})]/2}
$$

* $\rho_{I}$ 为中间 $2n$ 格点约化密度矩阵，$I=I_{1}\cup I_{2}$，$I_{1},I_{2}$ 各 $n$ 个连续格点；
* ${\mathcal R}_{I}$ 为以中央键为中心的镜像交换：${\mathcal R}_{I}|s_{1},\cdots,s_{2n}\rangle=|s_{2n},\cdots,s_{1}\rangle$；
* 热力学极限 $n\to\infty$ 下量子化：平庸 SPT 为 $+1$，拓扑 Haldane 为 $-1$，反铁磁（反射自发破缺）为 $0$；
* 随机测量读出用反射对称随机么正（镜像对共享 $U$），按 Hamming 距离加权，即原文 Eq.(3)；
* 变式与子系统取法见 [operator](../operator.md)。

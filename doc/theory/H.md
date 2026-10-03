# H

## 定义

SSH XXZ 链，$L$ 格点 OBC，格点编号 $1,\dots,L$。$X_{m},Y_{m},Z_{m}$ 为第 $m$ 格点上的 Pauli 算符。

$$
H(s,\delta)=H_{o}+H_{e}
$$

$$
H_{o}=(1-s)\sum_{j=1}^{L/2}h_{2j-1,2j},\qquad H_{e}=s\sum_{j=1}^{L/2-1}h_{2j,2j+1}
$$

$$
h_{kl}=e^{-\delta}(X_{k}X_{l}+Y_{k}Y_{l})+e^{+\delta}Z_{k}Z_{l}
$$

* $H_{o}$ 为奇键，$H_{e}$ 为偶键；
* $s$为二聚化参数，$\delta$ 为各向异性（$J_{xx}=e^{-\delta}$，$J_{z}=e^{+\delta}$；$\delta=0$ 为 Heisenberg 各向同性点，$\delta>0$ 偏 Ising）；

## 对称性分析

定义对称性算符:

$$
P=Z_{\rm tot}^{2}-\prod_{m=1}^{L}X_{m}-R
$$

* $H$ 及其分量 $H_{o},H_{e}$ 均与 $Z_{\rm tot}=\sum_{m=1}^{L}Z_{m}$、$\prod_{m=1}^{L}X_{m}$ 和全链反射 $R$（$m\leftrightarrow L+1-m$）对易。
* 由它们构成的演化算符保持这三个对称性(这关系到拟设的构建)，不发生对称性扇区跃迁，$P$ 守恒。
* $\delta\neq0$：$U(1)$ 对称（$Z_{\rm tot}$ 守恒）；$\delta=0$：$U(1)\to SU(2)$，增加总自旋平方 $S^{2}=\sum_{a=x,y,z}S_{a}^{2}$（$S_{a}=\frac12\sum_{m}A_{m}$，$A=X,Y,Z$）守恒，键内各向同性，与 ansatz 中 $\theta_{1}=\theta_{2}$ 对应。

## 对称性惩罚的 H'

为了筛选含有对称性的本征态(特别是有简并的时候), 可定义对称性惩罚的哈密顿量:

$$
H' = H + P
$$

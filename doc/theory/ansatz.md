# ansatz

orbit 拟设，格点编号 $1,\dots,L$.

## orbit 分组

全链反射 $R$：$m\leftrightarrow L+1-m$，镜面对映两键共用同一转角。记 $M=L/2$，奇键 $O_{j}=(2j-1,2j)$（$j=1,\dots,M$），偶键 $E_{j}=(2j,2j+1)$（$j=1,\dots,M-1$），配对规则为 $O_{j}\leftrightarrow O_{M+1-j}$，$E_{j}\leftrightarrow E_{M-j}$，至多一条中央键自镜像（$L=4k$ 时为偶键 $E_{M/2}$，$L=4k+2$ 时为奇键 $O_{(M+1)/2}$）。

## 单层演化

$$
U_{o}=\prod_{\alpha}\prod_{\langle kl\rangle\in\mathcal{O}_{\alpha}}e^{-i\theta_{o,\alpha,1}(X_{k}X_{l}+Y_{k}Y_{l})/2}e^{-i\theta_{o,\alpha,2}Z_{k}Z_{l}/2}
$$

$$
U_{e}=\prod_{\alpha}\prod_{\langle kl\rangle\in\mathcal{E}_{\alpha}}e^{-i\theta_{e,\alpha,1}(X_{k}X_{l}+Y_{k}Y_{l})/2}e^{-i\theta_{e,\alpha,2}Z_{k}Z_{l}/2}
$$

* $\langle kl\rangle$ 为格点 $k$ 与 $l$ 之间的键，$\alpha$ 为轨道编号；
* $\delta\neq0$ 时 $XX$ 与 $YY$ 共用 $\theta_{1}$（$Z_{\rm tot}$ 守恒），$ZZ$ 独立为 $\theta_{2}$；
* $\delta=0$ 时键内各向同性，$SU(2)$ 对称要求每个轨道 $\theta_{\alpha,1}=\theta_{\alpha,2}\equiv\theta_{\alpha}$，单层参数减半；
* 每个轨道一组 $(\theta_{1},\theta_{2})$，轨道总数 $M=L/2$，单层共 $L$ 参数（如 $L=8$ 时 8 参数，$\delta=0$ 时减半为 $L/2$），每键实现为 $RXX(t_{1})RYY(t_{1})RZZ(t_{2})$；
* 同一键内 $XX+YY$ 与 $ZZ$ 对易，子层内各键不交，对易；奇偶子层互不对易，必须保留两子层；
* 对本文使用的 $L=4k$（VQE 中 $L=8$）三个参考初态，拟设保持 $Z_{\rm tot}$、$\prod X$ 和 $R$，因此始终位于 $P=-2$ 扇区。

## 子层顺序

与初态配对重合的子层后作用：

* 平庸初态（奇键单态）：偶键先，即 $U_{o}U_{e}$；
* 拓扑初态（偶键单态为主）：奇键先，即 $U_{e}U_{o}$；
* AFM 初态：偶键先，即 $U_{o}U_{e}$。

多层拟设为各层依次作用在初态上，$U^{(1)}$ 最先作用，层间不反转顺序，所有层统一为：

$$
|\psi(\theta)\rangle=U^{(p)}\cdots U^{(2)}U^{(1)}|\psi_{\rm init}\rangle
$$

$$
U^{(l)}=U^{(l)}_{S}U^{(l)}_{F},\qquad l=1,\dots,p
$$

其中 $F$ 为先作用子层（平庸/AFM 初态 $F=e$，拓扑初态 $F=o$），$S$ 为另一子层，上标 $(l)$ 表示第 $l$ 层独立参数。实际作用顺序为 $F_{1}\to S_{1}\to F_{2}\to S_{2}\to\cdots\to F_{p}\to S_{p}$，相邻子层永远是不同类型。

有：

$$
N_{\theta}=\begin{cases}Lp,&\delta\neq0\\Lp/2,&\delta=0\end{cases}
$$

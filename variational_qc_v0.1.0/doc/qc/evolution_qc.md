# evolution qc

单层拟态 $|\psi(\theta)\rangle=U_{e}U_{o}|\psi_{\rm init}\rangle$ 或 $U_{o}U_{e}|\psi_{\rm init}\rangle$，以先作用子层命名顺序为准。

## 均匀参数（子层内共享）

其中 $\langle kl\rangle$ 表示格点 $k$ 与 $l$ 之间的最近邻键，$k,l$ 为格点/比特编号，$e/o$ 为偶/奇键集合。

$$
U_{e/o}=\prod_{\langle kl\rangle\in e/o}e^{-i\theta_{e/o,1}(XX+YY)/2}e^{-i\theta_{e/o,2}ZZ/2}
$$

* $S_{z}$ 守恒要求 $XX$ 与 $YY$ 共用 $\theta_{1}$，$ZZ$ 独立为 $\theta_{2}$；一层 4 参数 $(\theta_{o,1},\theta_{o,2},\theta_{e,1},\theta_{e,2})$，各向同性时退化为 2 个；
* 同一键内 $XX+YY$ 与 $ZZ$ 对易，键内顺序无关；奇偶键集合互不对易，必须保留两子层；
* 每键 $R_{xyz}$ 最少 3 个 CNOT，$L=8$ OBC 单层共 7 键；
* 拟态保持 $Z_{\rm tot}$ 与 $\prod X$，始终待在 $P=-1$ 扇区，最小化 $H$ 与 $H'$ 等价。

## 反射对称 orbit 参数（link 独立）

$R:j\to 7-j$，镜面对映两键共用同一转角。奇轨道 $\mathcal{O}_{\rm out}=\{(0,1),(6,7)\}$、$\mathcal{O}_{\rm in}=\{(2,3),(4,5)\}$；偶轨道 $\mathcal{E}_{\rm out}=\{(1,2),(5,6)\}$、$\mathcal{E}_{c}=\{(3,4)\}$（$(3,4)$ 自镜像）。

$$
U_{o}=\prod_{\alpha}\prod_{\langle kl\rangle\in\mathcal{O}_{\alpha}}e^{-i\theta_{o,\alpha,1}(XX+YY)/2}e^{-i\theta_{o,\alpha,2}ZZ/2}, \quad U_{e}=\prod_{\alpha}\prod_{\langle kl\rangle\in\mathcal{E}_{\alpha}}e^{-i\theta_{e,\alpha,1}(XX+YY)/2}e^{-i\theta_{e,\alpha,2}ZZ/2}
$$

* 单层 8 参数，每轨道继承 $(\theta_{\alpha,1},\theta_{\alpha,2})$；其余性质（键间对易、CNOT 计数、$P=-1$）与上一节相同。

## 子层顺序

与初态配对重合的子层后作用，先作用只给整体相位：

* 平庸初态（奇键单态）：偶键先，即 $U_{o}U_{e}$；
* 拓扑初态（偶键单态为主）：奇键先，即 $U_{e}U_{o}$；
* GHZ 初态：两种顺序等价，先上子层的 $\theta_{2}$ 浪费一个，余 3 参数有效。

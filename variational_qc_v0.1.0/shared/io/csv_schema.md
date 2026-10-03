# CSV 契约（Julia → Python）

主文件（以 task1 为例）：`task1_baseline/data/interim/tilde_ZR_L8_OBC.csv`，UTF-8，含表头。各任务同名文件落各自 `data/interim/`，schema 相同。

| 列 | 含义 |
|---|---|
| `s` | dimer 参数，`∈[0,1]` |
| `delta` | 各向异性参数，`∈[-3,3]` |
| `tilde_ZR` | 归一化 ZR，实数 |
| `is_degenerate` | 基态简并标志（`0/1`） |
| `Z_R` | （可选调试列）原始 `Tr(ρ_I R_I)` |
| `purity_I1` | （可选调试列）`Tr(ρ_{I1}^2)` |
| `purity_I2` | （可选调试列）`Tr(ρ_{I2}^2)` |

行序：`delta` 外层、`s` 内层，确定性排列。NPZ 可选附加，不得替代 CSV。

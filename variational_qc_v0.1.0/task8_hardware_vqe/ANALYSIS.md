# task8 真机 vs Aer-d1 O/S 三线对照结论

8 张三线图（解析 + Aer-d1 + 真机-d1，O/S × δ=±1 × sym/nosym）在
`data/figures/os/*_aer_*.png`。Aer 线由 task3/task5 thetas 经 statevector
精确导出（`scripts/derive_aer_os.py`，Q 复算全过）。

## 表达缺口 vs 硬件 penalty（分段读）

- **O（string）**：Aer-d1 的台阶比解析**更陡**（winner 切换是硬切换，
  解析是连续过渡）；真机跟得上形状，但 SPT 侧只爬到 ~0.4（解析 1.0）。
  结论：表达缺口小（Aer≈解析），penalty 几乎全是硬件的——8 体联合量
  对噪声最敏感。
- **S（结构因子）**：Aer-d1 紧贴解析线（表达缺口≈0）；真机整体下移
  ~0.05，形状保留。结论：均匀退极化式 penalty，与相无关。

## winner 分歧点清单（同点不同初态）

分歧全落在两初态近简并的交叉区（噪声翻转 winner，预期内）：

- sym 7 点：δ=−1 s=0.6（Aer triv / HW topo）；δ=+1 s=0.32–0.34
  （triv→afm）、s=0.86–0.92（topo→afm）。
- nosym 16 点：δ=−1 s=0.62（topo→triv）；δ=+1 s=0.16–0.34
  （triv→afm，连片）、s=0.86–0.92（topo→afm）。

三线图按各自 winner 画，分歧点已在图中自然呈现，不强行对齐。

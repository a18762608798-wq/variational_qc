# paper-map

按 `paper-outline.md` 将论文大纲归并到终稿宏观 feature，只列归属，不含写作细节。
Dxx 编号与产出去向以 `expriment-map.md` 为准，此处只引用不重复定义；
同一终稿宏观章节下的大纲小节默认合并；feature 编号按宏观叙事职责分配。

## Coverage

| 大纲节/宏观职责 | Feature | 消费 D | 上游实验 | 状态 |
|---|---|---|---|---|
| Methods：模型、拓扑物理量、变分电路、真机方法与误差缓解机制 | paper-01 | D01、D03、D04、D05、D06 | exp01、exp02、exp04 | in progress |
| Results and Discussion：优质比特具体排名、真机与模拟机结果及比较 | paper-02 | D07、D08 | exp04、exp05、exp06 | todo（D07/D08 图未出） |
| Closing：摘要、结论、统稿 | paper-03 | — | — | todo |
| Appendix：有限尺寸能隙曲线、交点和拟合等支持性诊断结果 | paper-04（特批，正文收敛后） | D02a/b/c | exp03 | deferred |

## Rules

- 一次开一个 feature，每个宏观 feature 走一轮完整循环（specify → clarify → plan → tasks → analyze → implement → converge）。
- 同一宏观终稿章节下的大纲小节默认合并，不因单个实验、图或 Dxx 单独创建 paper feature。
- Methods 只说明模型、协议、算法、测量和误差缓解机制；具体排名、趋势、比较和实验结论归 Results and Discussion。分析协议可在 Methods，分析所得结果归 Results 或 Appendix。
- 不得在 spec 之外另行定义主张与证据归属；Dxx 仍以 `expriment-map.md` 为准。
- Closing（paper-03）只在 Methods 与 Results and Discussion 完成主体收敛后开。
- Appendix（paper-04）不是默认 feature；D02a/b/c 属于支持性有限尺寸诊断，待正文 feature 收敛后创建。
- 缺件默认冻结对应结果、保留空位并登记 GAP；不阻塞无关章节。若结果解释不能由数据直接推出，登记 `GAP-INTERP [needs-user]` 并询问用户，不得自行猜测。

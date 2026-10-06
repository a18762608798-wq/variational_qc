# Constitution

## I. Spec 是论文定义的权威来源

任何影响主张内容、证据指向或结论口径的事项，都必须由对应
paper feature 的 spec 明确定义。

写作不得静默改变主张语义。
主张或证据发生变化时，应先更新 spec。

Spec 是持续维护的活文档，而不是一次性交付物。

## II. 主张必须绑定证据

- 每个正文主张（`CLM-###`）必须指向具体上游产物：数据集（`D##`）、
  图（`figs/` 文件）或共享输出（`S##`）。
- 无证据的主张不得以陈述句写入正文，只能以缺件（`GAP-###`）或
  标记的推测形式存在（见 IV）。
- 所有数字必须能在上游实验记录中溯源；禁止编造数字、p 值、
  引用、图表。

## III. 上游、成文与实现分离

- 上游 `scientific-computing`：实验定义与数值结果（`specs/expXX`、`S##`、`D##`）
- 本 preset 的 `spec.md`：论文定义（主张什么、用什么证据、缺什么）
- `plan.md`：章节→skill 映射与 LaTeX 工程方案
- `tasks.md`：具体写作与评审工作

上游实验定义不应重复写入论文 spec，需要时引用其 ID。
LaTeX 细节（宏包、编译命令）不应无必要进入 spec。

## IV. 缺件协议

缺件分两类，处理方式不同：

- `GAP-DATA`（缺数 / 缺图）：正文对应位置留
  `[TODO(GAP-###): 待 D##]` 空位，与之相关的主张冻结，
  不得用模糊措辞绕过。能写的部分（方法、背景、格式）先行。
- `GAP-INTERP`（依赖结果的解释性正文）：向用户要推测，
  写入 `[推测(user, 待 D## 验证)]` 并记录提出者与日期。
  推测在数据落定前不得改写为事实语气；
  `converge` 时必须转正（证据到位）或降级（删除 / 改为开放问题），
  不得过夜成事实。

## V. 引用必须来自读过的文献

- 每个引用（`CIT-###`）必须对应 Zotero 库中条目，
  且已通读到足以确认支撑引用处具体论述的程度（`paper-zotero-hunter`
  的 verify 标准）。
- 禁止为凑引用数量而引用未读文献；禁止编造 BibTeX。

## VI. Spec 必须清晰且可验证

- Spec 应区分面向作者的纸面描述与具有规范性的约束，并保持两者一致。
- 规范性约束应采用足以消除歧义、支持验证的最低必要形式化程度。
- 不得用多个彼此独立的表述重复定义同一规范性约束。

## VIII. 论文展开规则

以 `docs/paper-map.md`（由 `paper-map` skill 从 `paper-outline.md` 生成，
`Dxx` 定义以 `docs/expriment-map.md` 为准）为论文切分依据；
默认按终稿宏观章节创建 paper feature：`paper-01` 为 Methods，
`paper-02` 为 Results and Discussion，`paper-03` 为 Closing（摘要、结论、
统稿）。同一宏观章节下的多个大纲小节默认合并；`paper-04` Appendix
仅在材料足够独立且正文 feature 全部收敛后特批创建。
Methods 只说明模型、协议、算法、测量和误差缓解机制；具体排名、趋势、
比较和实验结论归 Results and Discussion。支持性有限尺寸诊断（如 D02a/b/c）
归 Appendix，不因其生成方法属于 Methods 就把结果结论混入 Methods。
一次展开一个 feature，每个走一轮完整 specify 流程
（specify → clarify → plan → tasks → analyze → implement → converge）；
不得把同一宏观章节默认拆成多个 feature，不得因单个实验、图或 Dxx
单独创建 paper feature；不得在 spec 之外另行定义主张与证据归属。

## IX. 论文技术与风格约定

| 域 | Skill |
| --- | --- |
| 全流程调度与缺件检查 | `paper-assembly` |
| 分节写作 | `paper-writing-section` |
| Related Work 对比 | `paper-writing-section`（Related Work 模式） |
| 组图进文（位置） | `paper-figure-layout` |
| 引用（Zotero 查缺 / 精读 / 入库） | `paper-zotero-hunter` |
| 套格式与 venue 规范（含 PRA） | `paper-latex-formatting` |
| 打分 | `paper-self-review` |
| 按意见改文 | `paper-revision` |

编译（`latexmk`）由 agent 直接执行，不经过 skill。
LaTeX 论文目录约定：`docs/paper/`（`main.tex`、`references.bib`、`figures/`、`output/`）。

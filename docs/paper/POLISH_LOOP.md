# Paper Polish Loop（PRA 文笔 + 内容丰富化）

- Venue：PRA（regular article）。Voice 以项目局部 `.opencode/skills/paper-latex-formatting/references/pra-writing-style.md` 为准，骨架以 `paper-writing-section` 为准。
- 指针：按 `docs/paper-map.md` 当前活动主线逐 feature 执行完整 spec-kit 流程（specify→clarify→plan→tasks→analyze→implement→converge），对象是文笔与内容丰富化，不新增 `CLM/CIT`，不编造数据。
- 当前活动主线为 `paper-01` Methods → `paper-02` Results and Discussion → `paper-03` Closing；`paper-04` Appendix 仅在正文收敛后按需创建。
- 打分：完成当前活动主线后用 `paper-self-review` 三 persona 打分并换算百分制；<80 进入下一轮；≥80 收敛。
- 非致命问题不中断 loop，记入下表，最后统一汇报。

## Rounds

| Round | 范围 | 状态 | 得分(/100) | 结论 |
|---|---|---|---|---|
| R1 | paper-01 → paper-07（EN 正文，ZH 同步顺延） | 完成 | 58 | 未达标，进 R2 |
| R2 | 定向补强（评审共识可改项：limitations 段 + 诚实 GAP 框架） | 完成 | 62 | 未达标，天花板为数据缺件，暂停待 D07/D08 |
| R3 | 背景+文献+公式扩充（目标 >50 篇，hunter 全流程） | 完成 | 68 | 未达标；背景杠杆已尽，停待 D07/D08 + ZH |
| R4 | 版式循环（skill 改 reprint 默认 + 单栏默认，D04 2×2 例外跨栏；paper-01→07） | 完成 | — | EN 9pp / ZH 7pp，0 未定义，无 overfull |
| R5 | 浮动体修复循环（pointer paper-03；spec 需改：paper-03 FIG-002 合图、paper-06 FIG-001–004 合占位） | 完成 | — | 真凶系 reprint 双栏 + 图多文短致队列堵塞（已对照排除 subfigure/size/floatfix）；解法：D06 三图合一 figure*（[p]，minipage 手工编号）+ D08 四占位合一 + 每节间 \FloatBarrier；全图归位，残留 stuck 警告为 barrier 强制冲刷所致，无实质影响 |
| R6 | 节压缩循环（11→8 节；pointer 经 paper-02/03/04/05/07） | 完成 | — | II MODEL AND SYMMETRIES；IV–V 并 PHASE MARKERS；VI–VII 并 VARIATIONAL STATE PREPARATION（终点降格为示意 subsection，05-points.tex 删除）；VIII–IX 并 HARDWARE IMPLEMENTATION；路线图重写；spec 同步 paper-03/04/05 SEC 输出 |
| R7 | analysis 债务执行 + 复检循环（pointer paper-01→07→01→07） | 完成 | — | 首轮修完 Round1 全部 7 项；复检新抓 3 处（paper-01 plan§3、paper-06 Contract F+plan、paper-07 CLM-003+plan§3）并清掉；终扫干净 |

## 历史 Feature 状态（R1，已归档）

| Feature | Sections | 状态 | 备注 |
|---|---|---|---|
| paper-01 | 01-model, 02-phasediagram, A-appendix | R1 完成 | where 从句 + 改写句 + 前向指针 |
| paper-02 | 03-sq, 04-heatmaps | R1 完成 | 改写句 + 面板枚举 + In contrast |
| paper-03 | 05-points, 06-ansatz | R1 完成 | 起点数值 + 构建两步法 + 自限句 |
| paper-04 | 07-premium | R1 完成（SEC-001） | 基准电路展开 + In contrast；SEC-002/GAP 冻结 |
| paper-05 | 08-readout | R1 完成 | where 从句 + 改写句 + 自限句 |
| paper-06 | 09-comparison | R1 完成（SEC-001） | 归一化理由 + 误差棒说明；SEC-002/GAP 冻结 |
| paper-07 | 00-introduction, 10-conclusion, abstract, 统稿 | R1 完成，R2 加 limitations 段 | 引言五步结构 + 摘要 moves；冻结结论未预支 |
| ISS-004 | paper-04/06 | R1 58 → R2 62，两轮均 <80；天花板为 D07/D08 数据缺件（Quality/Soundness 被锁），非文笔问题；loop 暂停，图到后由 paper-04/06 填图解冻并重跑打分 | loop 暂停待 exp05/exp06，恢复条件：`figs/exp05`、`figs/exp06` 落定 |
| ISS-005 | R3 | 8→51 篇正文引用，+弦序/阴影复杂度/TEE/VQE 代价函数公式；R3=68，仍<80；剩余扣分项为 D07/D08 数据（非文笔可解）与 ZH 未同步 | 背景杠杆已尽；不再空转文笔轮，恢复条件同 ISS-004，外加 ZH 同步排期 |

## 引用报告 R3：docs/paper/main.tex
- 目标 collection：paper-variational-qc（N7CLH4TB）
- 已确认：48 篇（全文已读到引用位置，支撑句见各 subagent 报告；den Nijs 由 agent 自读全篇确认）
  - SPT/纠缠：chen2011classification、pollmann2010entanglement、schuch2011classifying、li2008entanglement、levin2006detecting、kitaev2006topological、dennijs1989preroughening
  - VQE/训练：cerezo2021variational、tilly2022variational、mcclean2018barren、kandala2017hardware、campos2021abrupt、akshay2021parameter、mele2022avoiding、nemkov2025barren、bharti2021iterative、yu2023simulating
  - 测量/阴影：huang2020predicting、huang2021derandomization、hadfield2022measurements、zhou2023performance、elben2022toolbox、vitale2024robust、wang2023classical、kunjummen2023shadow、brydges2019probing
  - 缓解/基准：temme2017error、li2017efficient、nation2021scalable、mari2021extending、schultz2022analyzing、krebsbach2022optimization、gupta2024probabilistic、koenig2024inverted、ware2021experimental、qi2021randomized
  - 硬件/方法：colless2018robust、hempel2018quantum、google2020hartree、briegel2009measurement、sandvik2010computational
  - 既有 8 篇：su1979solitons、elben2020manybody、dennijs1989preroughening、peruzzo2014variational、raussendorf2001oneway、bravyi2021mitigating、sun2023efficient、satzinger2021realizing
- 条目-only（仅元数据级归属句，不承载技术内容）：haldane1983nonlinear、affleck1987rigorous、kandala2019error（Crossref 元数据已核，仅 Zotero 条目）
- 不相关/失败：0（arXiv ID 误判 4 个已在 harvest 阶段剔除，未引用）
- 验证工具故障：zotero 语义搜索 `Error finding id`（已记 Log，改关键词+collection 浏览）；revtex 对纯 eprint 条目报错，wang2023classical 改用 `journal={arXiv:ID}` 通过编译

## Issue Log（非致命，不中断）

| ID | Feature | 问题 | 处理 |
|---|---|---|---|
| ISS-001 | 全局 | ZH（`-zh.tex`）已同步 EN（R1–R3），3751 词，xelatex 编译通过，0 未定义 | 关闭 |
| ISS-002 | paper-04/06 | D07/D08 图缺件，排名论述与趋势结论保持冻结，只写方法口径 | 按 spec GAP 执行 |
| ISS-003 | 全局 | `02/03/05/09/10/A` 节零引用；按 paper spec 不新增未验证 `\cite`，缺口记 CIT 按需 | 待 hunter 排期，不阻塞 |

# scientific-computing preset

面向科学计算 / 数值实验的 Spec Kit 模板包。核心主张：**理论、实验定义与实现分离**，spec 是实验定义的权威来源。

## 文件

- `preset.yml` — manifest，声明 id / provides / replaces
- `templates/constitution-template.md` — 项目宪法：6 条原则（spec 权威、三层分离、feature 边界清晰、可重复可追溯、数值正确性优先于性能、技术风格映射到四个 scientific skills）
- `templates/spec-template.md` — 实验定义：科学问题 / 系统定义 / 参数 / 流程 P0x / 数值要求 / observables / VAL / 可重复性 / INV / 依赖
- `templates/plan-template.md` — 实现方案：Spec→实现映射、数值方法、数据结构、并行、Validation/Reproducibility Plan
- `templates/tasks-template.md` — 任务：按 Phase 推进，Performance 在 Validation 之后
- `commands/speckit.specify.md` — 从自然语言需求创建或更新 feature specification
- `commands/speckit.clarify.md` — 澄清 spec 中影响科学语义、边界、输出或验证的关键歧义
- `commands/speckit.plan.md` — 根据 spec 生成实现计划
- `commands/speckit.tasks.md` — 根据 spec 和 plan 生成可执行任务列表
- `commands/speckit.analyze.md` — 只读检查 spec / plan / tasks 的完整性、一致性与 constitution 符合度
- `commands/speckit.implement.md` — 实现、验证，验证通过后连续执行正式实验
- `commands/speckit.converge.md` — 审计实现与结果是否满足 spec / plan / tasks，剩余工作补回 tasks

## 标识约定

`P##` 实验步骤、`VAL-###` 验证标准、`INV-###` 实验不变量、`T###` 任务。跨文档用这些 ID 互引，避免同一事实写两份。

## 安装到项目

```bash
specify init --here --integration opencode # 初始化
specify preset add --dev ~/sync/computer/code/agent/specify/dev/scientific-computing --priority 5
specify preset resolve spec-template
```

具体的dev会被复制到 `.specify/presets/`

改完源目录后重装：

```bash
specify preset update scientific-computing --dev ~/sync/computer/code/agent/specify/dev/scientific-computing --priority 5
```

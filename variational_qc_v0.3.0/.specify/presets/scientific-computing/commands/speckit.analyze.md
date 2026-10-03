---
description: 只读检查当前 feature 的 spec、plan 和 tasks 是否完整、一致并符合 constitution。
---

# Analyze

## Workflow

1. 读取当前 feature 的：

   * `spec.md`
   * `plan.md`
   * `tasks.md`

2. 读取项目 live constitution。

3. 本命令严格只读。

   不修改：

   * `spec.md`
   * `plan.md`
   * `tasks.md`
   * 代码

4. 检查 Constitution Alignment：

   * spec、plan、tasks 是否违反 constitution；
   * feature 是否出现明显职责重叠；
   * 是否存在未记录但影响科学结果的隐式条件；
   * 是否存在以性能或实现便利改变科学语义的设计。

5. 检查 Spec → Plan：

   * plan 是否覆盖 spec 所需的实现工作；
   * plan 是否静默修改实验参数、边界、输出或验证定义；
   * plan 是否引入本应先写回 spec 的科学决定；
   * plan 的验证方案是否覆盖 spec 中的 validation。

6. 检查 Plan → Tasks：

   * plan 中必要的实现工作是否都有对应任务；
   * validation 是否有对应任务；
   * tasks 是否引入 plan 中没有的架构或实现决策；
   * 是否存在重复、无意义或超出当前 feature 边界的任务。

7. 检查 Spec → Tasks：

   * spec 的关键输出是否最终能够由任务实现；
   * spec 的 validation 是否全部有执行路径；
   * 是否存在 Implementation 完成但科学有效性无法验证的情况。

8. 检查未解决问题：

   * spec 中是否仍有阻塞性 Open Questions；
   * plan 中是否存在阻塞实现的未解决问题；
   * tasks 是否错误地绕过这些问题继续实施。

9. 检查一致性与漂移：

   * 同一个参数、术语或条件在不同文档中是否含义不同；
   * 已经被 spec 修改的旧设计是否仍残留在 plan/tasks；
   * 是否存在互相矛盾的验证标准；
   * 是否存在重复定义同一职责的内容。

10. 对发现的问题按严重程度分类：

* `CRITICAL`：违反 constitution，或可能导致科学语义错误 / 无法判断结果有效；
* `HIGH`：spec、plan、tasks 之间存在明确冲突或关键覆盖缺失；
* `MEDIUM`：会造成实施歧义、重复工作或明显维护问题；
* `LOW`：非阻塞性的清晰度或结构改进。

 1. 输出简洁报告：

| ID | 严重度 | 位置 | 问题 | 应在哪一层修正 |
| -- | --- | -- | -- | ------- |

并补充：

* Spec → Plan coverage
* Validation coverage
* Unmapped tasks
* Constitution conflicts
* Blocking Open Questions

 1. 不直接修复问题。

指出问题应回到哪个阶段处理：

* 实验定义问题 → `specify` / `clarify`
* 实现设计问题 → `plan`
* 任务拆分问题 → `tasks`

如果不存在实质问题，明确报告 artifacts 一致，可以进入 `implement`。

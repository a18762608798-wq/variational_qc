---
description: 根据当前 feature 的 spec 和 plan 生成可执行任务列表。
---

# Tasks

## Workflow

1. 读取当前 feature 的：
   - `spec.md`
   - `plan.md`

2. 读取项目 live constitution，并遵守其中约束。

3. 解析当前生效的 `tasks-template`，据此生成 `tasks.md`。

4. 将 plan 拆成具体、可执行、可验证的任务。
   - 每个任务应描述明确的工作结果。
   - 任务粒度应足以独立完成和检查。
   - 不要为了形式化而生成不必要的任务。
   - 不要机械复制 plan 的章节标题。

5. `Implementation` 只包含实现当前 plan 所需要的工作。
   - 保持 feature 边界。
   - 遵循 plan 中已经确定的模块与技术方案。
   - 不在 tasks 阶段重新设计架构，除非 plan 明显无法执行。

6. `Validation` 必须覆盖 spec 中定义的验证要求和 plan 中的验证方案。
   - 实现任务完成不等于 feature 完成。
   - 必须包含足以判断科学 / 数值结果是否有效的验证任务。

7. 如果在拆分任务过程中发现：
   - 实验定义缺失；
   - 参数或边界条件不明确；
   - plan 与 spec 冲突；
   - 必须做出会改变实验语义的新决定；

   不要在 `tasks.md` 中自行补充。

   应将该问题反馈到 spec 或 plan 层处理。

8. `Follow-up` 仅在存在明确的非阻塞后续工作时生成。
   没有内容时删除该 section。

9. 删除：
   - 未替换的模板占位符；
   - 空章节；
   - 重复任务；
   - 与当前 feature 无关的任务。

10. 完成前检查：
    - 所有 Implementation 任务均来自 plan；
    - 所有必要 Validation 均被覆盖；
    - 没有新增实验定义；
    - 没有与其他 feature 重复职责；
    - 每个任务都有明确完成条件。

完成后报告 `tasks.md` 路径，以及是否存在阻塞实施的问题。

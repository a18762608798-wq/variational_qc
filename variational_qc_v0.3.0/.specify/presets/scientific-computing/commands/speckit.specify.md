---
description: 从自然语言需求创建或更新科学计算 feature specification。
---

# Specify

## User Input

`$ARGUMENTS`

用户输入不能为空。

## Workflow

1. 读取项目 live constitution，并遵守其中的全部约束。

2. 检查 `specs/` 下已有 feature。
   - 如果需求属于现有 feature 的自然扩展，更新该 feature。
   - 只有当需求具有独立职责时才创建新的 feature。
   - 避免创建职责重叠的 feature。

3. 确定 feature directory。
   - 更新已有 feature 时使用已有目录。
   - 新建时按照项目现有命名和编号方式创建目录。

4. 解析当前生效的 `spec-template`。
   - 新建 feature 时以该模板创建 `spec.md`。
   - 更新 feature 时保留已有有效内容，只修改本次需求涉及的部分。

5. 根据用户输入和现有项目上下文填写 `spec.md`。
   - 严格遵循 template 的章节和职责。
   - 不在 specification 阶段进行实现设计。
   - 不为填满模板而制造信息。

6. 对影响实验语义、结果解释或可重复性的缺失信息：
   - 不自行猜测；
   - 无法可靠确定时记录到 `Open Questions`。

7. 删除无内容的按需章节和未替换的模板占位符。

8. 更新 `.specify/feature.json` 指向当前 feature directory。

9. 检查最终 spec：
   - 与 constitution 一致；
   - 与已有 feature 无不必要职责重叠；
   - 没有混入 plan 层的实现细节；
   - 没有未经依据猜测的科学参数。

完成后报告 spec 路径，以及是否存在阻塞性的 Open Questions。

---
description: 根据当前 feature specification 生成实现计划。
---


<!-- Source: scientific-computing -->
# Plan

## Workflow

1. 读取当前 feature 的 `spec.md`。

2. 读取项目 live constitution，并遵守其中约束。

3. 解析当前生效的 `plan-template`。

4. 根据 `spec.md` 生成 `plan.md`。
   - 严格遵循 plan template。
   - 不重新定义实验语义。
   - 不修改 spec 中的参数、边界、输出或验证条件。
   - 如发现 spec 不足以支持实现计划，将问题记录为未解决问题，而不是自行补充实验定义。

5. 规划代码与模块结构时：
   - 遵守项目指定的代码架构 Skill。
   - 保持 feature 职责边界。
   - 优先复用已有稳定能力，避免与其他 feature 重复实现。
   - 不为了抽象而提前创建共享框架。

6. 数值与技术决策只记录实现层选择。
   如果某个决定会改变实验语义或科学结果，应回到 spec 修改，而不是仅写入 plan。

7. 验证方案必须覆盖 spec 中定义的验证要求。

8. 删除无意义的占位内容和空章节。

完成后报告 `plan.md` 路径，以及是否存在阻塞实现的未解决问题。
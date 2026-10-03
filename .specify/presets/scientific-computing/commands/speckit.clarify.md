---
description: 澄清当前 feature specification 中影响科学语义、边界、输出或验证的关键歧义。
---

# Clarify

## Workflow

1. 读取当前 feature 的 `spec.md`。

2. 读取项目 live constitution，并遵守其中约束。

3. 检查 spec 是否存在会实质影响后续 plan、implementation 或 validation 的缺失或歧义，重点检查：

   * 目标是否明确；
   * feature 边界与依赖是否明确；
   * 实验 / 计算定义是否足以确定科学语义；
   * 关键参数、输入、初始条件或边界条件是否缺失；
   * 输出和 observable 是否明确；
   * validation 和 invalid-run 条件是否足以判断结果有效；
   * `Open Questions` 中是否存在阻塞性问题。

4. 不询问纯实现层问题，例如：

   * 文件如何拆分；
   * 使用什么模块结构；
   * API 如何设计；
   * CPU / GPU 如何实现；
   * 普通代码风格选择。

   这些属于 plan 或 implementation。

5. 只询问真正需要用户决定且无法从已有上下文可靠确定的问题。

   * 每次只问一个问题；
   * 优先处理影响最大的歧义；
   * 最多询问 5 个问题；
   * 已经明确的信息不要重复询问。

6. 每获得一个明确答案后：

   * 直接更新 `spec.md` 中最合适的现有章节；
   * 如果答案解决了 `Open Questions` 中的对应问题，删除该问题；
   * 不保留已经失效或互相矛盾的旧描述；
   * 不额外创建澄清历史章节。

7. 不自行猜测会改变科学语义的内容。

8. 如果剩余问题只影响实现方式而不影响 spec，则停止澄清并留给 plan。

9. 完成后重新检查 spec：

   * 是否仍存在阻塞性歧义；
   * 是否出现内部矛盾；
   * 是否仍有无法判断结果有效性的缺口；
   * 是否与 constitution 冲突。

如果没有值得正式澄清的关键问题，不修改 spec，直接报告可以继续进入 plan。

完成后报告：

* 更新的 `spec.md` 路径；
* 本次解决了多少个问题；
* 是否仍存在阻塞性的 Open Questions。

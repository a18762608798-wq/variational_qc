# Spec Delta

## ADDED Requirements

### Requirement: 真机 sym/nosym full 五线画布

系统 SHALL 对 task8 sym 与 nosym 任务、每条 `δ` 切线各渲染一个 full 画布：
解析 `E0`/`E1` + 真机三初态 cost（triv/topo/afm 各一线，共 5 线），
横轴 `s∈[0,1]`，纵轴能量绝对值（与既有同类画布同语言），标题保留
hw 标识、任务标识（sym/nosym）、`δ` 取值与方法标识、无边界条件字样，
落盘为 PNG（必选）与 PDF（可选同名）于 task8 figures 目录（文件名 SHALL 含
`hw_{sym,nosym}_full` 与 `δ` 标识）；输入缺失或缺列时 SHALL 以非零退出码失败
且不产生残缺图片。

#### Scenario: 三分量分化可判读

- **WHEN** 并排查看同 `δ` 下 task3 Aer full 画布与本画布
- **THEN** 每图 5 线齐全图例可分；各初态真机相对 Aer 的上移量如实呈现
  （均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

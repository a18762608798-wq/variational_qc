# Spec Delta

## ADDED Requirements

### Requirement: Aer-d1 O/S 分量导出

系统 SHALL 由 task3/task5 depth-1 获胜 theta 经 statevector 精确计算
每点 O_norm/S_norm（定义与 task8 一致），winner 口径 SHALL 与 task8
一致（E 最优初态），存 `vqe_{sym,nosym}_OS_aer_L8_OBC.csv`
（表头 `s,delta,O_norm,S_norm`，行数 102，行序 delta 外层、s 内层）；
导出 SHALL 确定性（两次运行逐位一致）。

#### Scenario: 与 task8 口径一致

- **WHEN** 对比同点 Aer O/S 与 task8 真机 O/S
- **THEN** 两者 winner 初态相同、行序相同，可直接逐点相减得 penalty

### Requirement: O/S 三线对照画布

系统 SHALL 对 O 与 S、δ=±1、sym/nosym 各渲染三线对照图
（解析 Ostr/Spi + Aer-d1 + 真机-d1，共 8 张），横轴 `s∈[0,1]`，
纵轴与既有 O/S 画布同语言，标题保留 aer/hw 标识、任务标识、
`δ` 取值、无边界条件字样，落盘 PNG（必选）与 PDF（可选同名）于
task8 figures/os/（文件名 SHALL 含 `aer` 标识）；输入缺失或缺列时
SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: 表达与噪声分离可判读

- **WHEN** 查看任一张三线图
- **THEN** 解析/Aer/真机三线齐全图例可分；Aer 偏离解析 = 表达缺口，
  真机偏离 Aer = 硬件 penalty，两段可分读（均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行导出与绘图两次
- **THEN** 两次输出逐位/逐像素一致，原子写出不残留半文件

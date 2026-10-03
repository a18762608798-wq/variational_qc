# viz/vqe-comparison Specification

## Purpose

把三初态 VQE 最优与解析能谱画在同一画布上，使"谁在哪个相区贴住基态"一目了然；只消费 VQE 目标值 CSV 与解析谱 CSV 做渲染。

## Requirements

### Requirement: 五线对照画布

系统 SHALL 对每条 `δ` 切线渲染一个画布：解析 `E0`、`E1`（取自 task1 解析谱 CSV）两条线 + 三初态 VQE 最优（取自 VQE 目标值 CSV）三条线，共 5 线，横轴 `s∈[0,1]`、纵轴绝对能量，含轴标签、图例与标题（标题保留 `δ` 取值与方法标识、无边界条件字样），落盘为 PNG（必选）与 PDF（可选同名）；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片；共 SHALL 输出两个画布（`δ=-1`、`δ=+1` 各一）。

#### Scenario: 相区贴合可判读

- **WHEN** 查看任一画布
- **THEN** 5 线齐全且图例可区分；各初态线在其对应相区贴近 `E0`，偏离本身记为结论

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

### Requirement: 三线 min-VQE 对照画布

系统 SHALL 对每条 `δ` 切线另渲染一个三线画布：解析 `E0`、`E1`（取自 task1 解析谱 CSV）两条线 + `min(VQE)` 一条线（同点三初态目标值逐点取最小，纯文件后处理、不得重跑优化），共 3 线，横轴 `s∈[0,1]`、纵轴绝对能量，含轴标签、图例与标题（标题保留 `δ` 取值与方法标识、无边界条件字样），落盘为 PNG（必选）与 PDF（可选同名），文件名 SHALL 与五线图区分；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片；共 SHALL 输出两个画布（`δ=-1`、`δ=+1` 各一）。

#### Scenario: min 线包络可判读

- **WHEN** 查看任一三线画布
- **THEN** 3 线齐全且图例可区分；`min(VQE)` 线逐点不高于任一初态线、不低于 `E0 − 1e-6`（变分上界性）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

### Requirement: 双线 VQE-Q 对照画布

系统 SHALL 对每条 `δ` 切线另渲染一个双线画布：解析 `Q`（取自 task1 `Q_L8_OBC.csv`）+ `Q_vqe`（取自 VQE-Q CSV），共 2 线，横轴 `s∈[0,1]`、纵轴 `Q`（范围 `[-1,1]`，与 task1 Q 热力图同语言），含轴标签、图例与标题（标题保留 `δ` 取值与方法标识、无边界条件字样），落盘为 PNG（必选）与 PDF（可选同名），文件名 SHALL 与现有四图区分；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片；共 SHALL 输出两个画布（`δ=-1`、`δ=+1` 各一）。

#### Scenario: 相落点可对照

- **WHEN** 查看任一双线画布
- **THEN** 2 线齐全且图例可区分；`Q_vqe` 与解析 `Q` 同语言可比，偏离本身记为结论

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

### Requirement: 双线 VQE-ZR 对照画布

系统 SHALL 对每条 `δ` 切线另渲染一个双线画布：解析 `tilde_Z_R`（取自 task1 `tilde_ZR_L8_OBC.csv`）+ `ZR_vqe`（取自 VQE-ZR CSV），共 2 线，横轴 `s∈[0,1]`、纵轴 `tilde_Z_R`（范围 `[-1.2,1.2]` 物理带），含轴标签、图例与标题（标题保留 `δ` 取值与方法标识、无边界条件字样），落盘为 PNG（必选）与 PDF（可选同名），文件名 SHALL 与现有六图区分；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片；共 SHALL 输出两个画布（`δ=-1`、`δ=+1` 各一）。

#### Scenario: 相落点可对照

- **WHEN** 查看任一双线画布
- **THEN** 2 线齐全且图例可区分；`ZR_vqe` 与解析 `tilde_Z_R` 同语言可比，偏离本身记为结论

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

### Requirement: 逐深度画布组

系统 SHALL 对每个深度（`n ∈ {2,3,4,5}`）、每条 `δ` 切线渲染三个画布：min-energy 三线（解析 `E0`/`E1` + 该深度 `min(VQE)`）、Q 双线（解析 `Q` + 该深度 `Q_vqe`）、ZR 双线（解析 `tilde_Z_R` + 该深度 `ZR_vqe`），其中 `Q_vqe`/`ZR_vqe` SHALL 由该深度获胜 thetas 经既有派生定义纯后处理得到（不得重跑优化）；各画布横轴 `s∈[0,1]`，纵轴与既有同类画布同语言（能量绝对值、Q `[-1,1]`、ZR `[-1.2,1.2]`），标题保留深度、`δ` 取值与方法标识、无边界条件字样，落盘为 PNG（必选）与 PDF（可选同名）于该深度专属 figures 目录（文件名 SHALL 含深度标识，不得与 task3 或其他深度混淆）；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: depth scaling 可判读

- **WHEN** 并排查看同一 `δ` 下各深度的 min-energy 画布
- **THEN** 每图 3 线齐全图例可分；过渡区缺口随深度的变化如实呈现（闭合或不闭合均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

### Requirement: nosym 逐深度画布组

系统 SHALL 对每个深度（`{1,5}`）、每条 `δ` 切线渲染三个画布：min-energy 三线（解析 `E0`/`E1` + 该深度 `min(VQE-nosym)`）、Q 双线（解析 `Q` + 该深度 `Q_vqe`）、ZR 双线（解析 `tilde_Z_R` + 该深度 `ZR_vqe`），纵轴与既有同类画布同语言（能量绝对值、Q `[-1,1]`、ZR `[-1.2,1.2]`），标题保留 nosym 标识、深度、`δ` 取值与方法标识、无边界条件字样，落盘为 PNG（必选）与 PDF（可选同名）于本任务该深度专属 figures 目录（文件名 SHALL 含 nosym 与深度标识，不得与其他任务混淆）；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: 简化代价可判读

- **WHEN** 并排查看同深度同 `δ` 下 nosym 与 task3/4 对称版画布
- **THEN** 每图线齐全图例可分；能量缺口与相落点偏移如实呈现（均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件


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


### Requirement: 真机 O/S 分量输出与对照画布

系统 SHALL 由既有 Z 基计数合成 `O_norm / S_norm / <O_str> / <S(pi)>`
（与 Q 同定义，整串联合估计），存入
`vqe_{sym,nosym}_OS_L8_OBC.csv`（表头
`s,delta,O_norm,S_norm,O_str_raw,S_pi_raw`，行数 102，行序 delta 外层、
s 内层；已有 CSV 表头 SHALL NOT 改动）；并对 O 与 S 各渲染对照画布
（解析线 task1 `Ostr/Spi` + 真机线），O/S × δ=±1 × sym/nosym 共 8 张，
落盘为 PNG（必选）与 PDF（可选同名）于 figures/os/ 子目录；
输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: 分量行为可见

- **WHEN** 查看 O（或 S）对照画布
- **THEN** 解析线与真机线齐全图例可分；string 序参的塌陷位置
  （或结构因子峰的剩余高度）如实呈现（均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行合成与绘图两次
- **THEN** 两次输出逐位/逐像素一致，原子写出不残留半文件

### Requirement: figures 目录分类

系统 SHALL 将 task8 figures/ 下图片按类归入子目录：`min/`、`q/`、
`full/`、`os/`；现有 16 张 SHALL 按类搬入（文件名语义不变，只换目录）；
新 O/S 8 张 SHALL 直接落 `os/`。

#### Scenario: 旧图可找

- **WHEN** 按旧知识找某张已验收的图
- **THEN** 同名文件在对应子目录存在，无重名冲突、无残留散文件


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

### Requirement: orbit 逐深度画布组

系统 SHALL 对每个深度（`n ∈ {1,2,3}`）、每条 `δ` 切线渲染三个画布：min-energy 三线（解析 `E0`/`E1` + 该深度 `min(VQE-orbit)`）、Q 双线（解析 `Q` + 该深度 `Q_vqe`）、ZR 双线（解析 `tilde_Z_R` + 该深度 `ZR_vqe`），其中 `Q_vqe`/`ZR_vqe` SHALL 由该深度获胜 orbit thetas 经既有派生定义纯后处理得到（不得重跑优化）；各画布横轴 `s∈[0,1]`，纵轴与既有同类画布同语言（能量绝对值、Q `[-1,1]`、ZR `[-1.2,1.2]`），标题保留 orbit 标识、深度、`δ` 取值与方法标识、无边界条件字样，落盘为 PNG（必选）与 PDF（可选同名）于本任务该深度专属 figures 目录（文件名 SHALL 含 orbit 与深度标识，不得与 task3/task4 或其他深度混淆）；输入缺失或缺列时 SHALL 以非零退出码失败且不产生残缺图片。

#### Scenario: orbit 效应可判读

- **WHEN** 并排查看同一 `δ` 下 orbit 各深度的 min-energy 画布，并与 task3/4 同深度 uniform 画布对照
- **THEN** 每图线齐全图例可分；orbit 相对 uniform 的能量贴合差与 `Q`/`ZR` 相落点偏移如实呈现（均为结论）

#### Scenario: 确定性输出

- **WHEN** 同一输入运行绘图两次
- **THEN** 两次输出逐像素一致，原子写出不残留半文件

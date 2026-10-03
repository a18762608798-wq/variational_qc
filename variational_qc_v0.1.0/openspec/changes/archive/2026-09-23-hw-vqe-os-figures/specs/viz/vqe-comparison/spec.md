# Spec Delta

## ADDED Requirements

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

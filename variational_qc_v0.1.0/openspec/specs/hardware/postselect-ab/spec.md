# hardware/postselect-ab Specification

## Purpose

对 task8 真机三基计数做对称性后选择，输出后选择版 H/Q/O/S 数据与对照画布，量化洗掉对称性破缺成分后的相落点变化；零机时纯后处理。

## Requirements

### Requirement: 方案 A 洗 O/S/Q

系统 SHALL 对每点 Z 基计数只留 M=0（8 比特中 1 的个数为 4）的字符串，
用保留子集重算 O_norm、S_norm（整串联合估计，与裸定义一致）并合成 Q；
Q/O/S 的获胜初态 SHALL 按 H_post 的 argmin 确定（后选择数据集内部自洽，
不沿用裸 E 的 winner）；保留率 SHALL 单独存诊断 CSV
（每点 M=0 占比）。

#### Scenario: 洗完可比

- **WHEN** 并排查看同 δ 下裸 Q 画布与后选择 Q 画布
- **THEN** 线齐全图例可分；过渡区偏移如实呈现（均为结论）

#### Scenario: 空集不崩

- **WHEN** 某点 M=0 保留数为 0（极端噪声）
- **THEN** 该点记 NaN 并如实进报告，不中断全量合成（非零退出码仅用于
  输入缺失，不用于空集）

### Requirement: 方案 B 洗 H

系统 SHALL 对每点三基计数分别过滤——Z 基留 M=0 算 ZZ 相关、
X/Y 基留偶数个 1 算 XX/YY 相关——按 H 系数拼出 H_post；
H_post SHALL 标注为诊断量，SHALL NOT 用于变分上界判断；
三基宇称通过率 SHALL 进诊断 CSV。

#### Scenario: 上界声明

- **WHEN** 查看 H_post 画布或 CSV
- **THEN** 其标题/表头或附注 SHALL 声明"诊断量，非变分上界"

### Requirement: 输出结构对标 task8

系统 SHALL 落盘：后选择版 E CSV（H_post 分初态列，102 行，行序与
task3 一致）、Q CSV、OS CSV（O_norm/S_norm/O_str_raw/S_pi_raw）、
保留率诊断 CSV；min/Q/full/os 四组对照画布（PNG 必选 + PDF 可选），
figures/ 下同样 min/q/full/os 分类；合成与绘图 SHALL 确定性
（两次运行逐位/逐像素一致），原子写出。

#### Scenario: 体例一致

- **WHEN** 并排查看 task8 与本任务同类文件
- **THEN** 表头、行序、命名体例、纵轴语言一致，可直接并排判读

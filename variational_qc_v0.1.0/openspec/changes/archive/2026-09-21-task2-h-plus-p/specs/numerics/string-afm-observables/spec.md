# Spec Delta

## ADDED Requirements

### Requirement: task2 派生复用

系统 SHALL 对 task2 基态存档复用既有 derive 定义（`O_str`、`S(π)`、归一化、`Q` 公式与 CSV schema 不变，文件名不变、落盘于 task2 专属目录）：`tilde_ZR` CSV 改为 task2 存档派生，`O_str`/`S_pi`/`Q` CSV 链路同 task1；`Ostr`/`Spi` 的 CSV SHALL 输出（`Q` 依赖其归一列），但不为其画热力图；`S(q)` 曲线 SHALL 跳过。

#### Scenario: 链路同构

- **WHEN** 以默认配置运行 task2 derive 全链
- **THEN** 产出 `tilde_ZR`、`Ostr`、`Spi`、`Q` 四个 CSV（各 `10000` 行，行序与 task2 存档一致），无 `S(q)` 产物

### Requirement: task1/task2 一致性验证

系统 SHALL 逐行对比 task1 与 task2 的四个 CSV（`tilde_ZR`、`O_str_norm`、`S_pi_norm`、`Q` 列）：一致 SHALL 定义为差值绝对值 `≤ 1e-8`；验证 SHALL 输出 pass/fail 结论与差异行清单（`s,delta,列,两值`）；`energies` 差 −1 为预期、不参与 fail 判定；`is_degenerate` 翻转的行 SHALL 单独列出、不判失败（P 劈裂简并子空间为预期内效应）。

#### Scenario: 不变即通过

- **WHEN** 四个对比列全部逐行一致且无能量异常行
- **THEN** 结论为通过，对称性预期成立

#### Scenario: 差异如实记录

- **WHEN** 任一对比列出现超容差行，或能量差偏离 −1
- **THEN** 结论为不通过并列出全部差异行（含坐标与两值），差异本身记为结论（P 选择效应的实证），不得静默截断或放宽容差

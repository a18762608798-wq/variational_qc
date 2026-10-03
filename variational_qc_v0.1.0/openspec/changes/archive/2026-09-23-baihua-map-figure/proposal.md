# Proposal

## Why

task6/task7 选出的冠军链、候选环、环内最佳子链散在 JSON 里，没有一张图能一眼看出它们在芯片上的位置关系。quark 官图 `save_svg_fname` 在无头环境静默失败，且只支持单组节点高亮、无法区分多类标记——需要一张自己的 Baihua 链接图，把底噪（T1/耦合保真度）与三类标记画在一起。

## What Changes

- 新增 `task7_ring_select/scripts/plot_baihua_official.py`：拦截 quark 官图绘制，在其坐标系上叠加标记后落盘。
- 官图底图：节点色 = T1，边色 = CZ 保真度（带边编号与双色标）；标题 Baihua。
- 三类标记（只标最好，不标前几）：红 = 最好的链 `[67..74]`；蓝 = 最好的环
  Baihua `[125,126,127,128,129,142,141,140,139,138]`（含闭合边）；
  绿 = 最好环里最好的 8-子链 `[126,127,128,129,142,141,140,139]`。
- 产物：`task7_ring_select/data/figures/baihua_official_map.png`（英文图例）。
- 脚本已写完跑通，本 change 做正式立项与验收。

## Capabilities

### New Capabilities

- `viz/baihua-topology-map`: 由拓扑快照渲染 Baihua 链接图，叠加冠军链/候选环/最佳子链三类标记。

### Modified Capabilities

（无）

## Impact

- 新增脚本 1 个 + PNG 产物 1 张；无真机提交、无机时消耗。
- 无现有代码改动（qmeas 库不动）。

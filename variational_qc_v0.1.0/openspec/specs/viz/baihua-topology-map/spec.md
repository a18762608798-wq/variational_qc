# viz/baihua-topology-map Specification

## Purpose

把 Baihua 拓扑快照画成一张可判读的链接图，让冠军链、候选环、环内最佳子链的位置关系一目了然，供后续真机实验选区参考。

## Requirements

### Requirement: 链接图渲染与三类标记

系统 SHALL 以 quark 官图为底（拦截绘制后叠加标记再落盘）：节点色 SHALL 为 T1，边色 SHALL 为 CZ 保真度；图上 SHALL 只叠加三组最优标记——红为最好的链 `[67..74]`，蓝为最好的环 Baihua `[125,126,127,128,129,142,141,140,139,138]`（含闭合边），绿为最好环里最好的 8-子链 `[126,127,128,129,142,141,140,139]`；图例 SHALL 为英文；产物 SHALL 落盘为 PNG。

#### Scenario: 标记齐全可分

- **WHEN** 打开 baihua_official_map.png
- **THEN** 红/蓝/绿三类线与图例一一对应，官图底图（T1/CZ 保真度双色标）完整保留

#### Scenario: 离线可复现

- **WHEN** 用同一快照重跑脚本
- **THEN** 零网络请求，产物逐像素一致（快照不变则输出不变）

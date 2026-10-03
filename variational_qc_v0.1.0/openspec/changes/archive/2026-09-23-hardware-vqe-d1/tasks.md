# Tasks

## 1. task8 骨架与电路验证

- [x] 1.1 建 `task8_hardware_vqe/` 目录（config+scripts+data+README；解释器复用 qmeas env），写三基测量电路构造（拟态+X/Y/Z 旋转、coupling pin 线性/环闭合、读出纠错开），O3 转译抽查 CZ 数不增、深度收敛，用 Aer 验证逐点 H/Q 与 task3/5 获胜值一致（容差 1e-9），零真机提交
- [x] 1.2 提交当天 force 重拉拓扑验映射比特存活，产出 612 点提交清单，人工确认账单（612×3×1024）后进入提交

## 2. 真机提交与轮询

- [x] 2.1 一次性全提交（两阶段），验证全部缺失电路进入轮询（tids 落盘）
- [x] 2.2 统一轮询收回 + Failed 对账，验证每点 3 份结果齐全（缺失只补缺口）

## 3. 存档与对照

- [x] 3.1 合成 H/Q/P 目标值 CSV（行数 102，行序与 task3 一致），min-energy 与 Q 对照画布（去 ZR）落盘
- [x] 3.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档

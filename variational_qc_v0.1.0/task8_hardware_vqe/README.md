# task8 真机单层 VQE 前向测量

## 解释器

用 `03_tools_practice/qmeas` 项目 env 的 python：

```bash
QPY=../../03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
```

## 内容

- `scripts/circuits.py`：拟态制备（复用 task3/task5）+ X/Y/Z 测量基电路；
  sym-topo 走 10 比特环电路（桥比特 `{125,138}` 经三跳 SWAP 连 0-7）。
- `scripts/analysis.py`：三基计数 → H 期望、Q、P 两项（端序已核对）。
- `scripts/verify_aer.py`：Aer 一致性（精确 36 点 + 计数 12 点 + Q 12 点 + 环单态）。
- `scripts/submit.py`（2.1 写）：612 点 × 3 基一次全交。

## 流程

1. `$QPY scripts/verify_aer.py`（零机时，已通过）。
2. 提交当天验存活 + 账单确认（1.2）。
3. `submit.py` 真机提交 → 轮询 → CSV + 对照画布（去 ZR）。

#!/usr/bin/env python
"""task4 逐深度 Q/ZR 派生：获胜 thetas 重建电路，求 Q 与 tilde_ZR.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task4_vqe_depth/scripts/derive_depth_qzr.py --depth K

纯后处理，不做优化。输出 depthK/data/interim/vqe_Q_L8_OBC.csv 与
vqe_ZR_L8_OBC.csv（各 102 行，s,delta + 值列）。算子复用 task3 实现。
"""

import argparse
import csv
import json
import os
import sys

_HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)  # task4 ansatz（含 n_layers）优先
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(_HERE)),
                                "task3_vqe", "scripts"))  # observables/zr_obs 复用

from ansatz import build_vqe_circuit, statevector_of  # noqa: E402  task4 版
from observables import Q_of_state  # noqa: E402
from zr_obs import tilde_ZR_of_state  # noqa: E402

import ansatz as _ax  # noqa: E402,F401  确认 task4 版（含 n_layers）

assert "n_layers" in open(os.path.join(_HERE, "ansatz.py")).read()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, required=True)
    args = ap.parse_args()
    k = args.depth
    root = f"task4_vqe_depth/depth{k}/data/interim"
    th_path = f"{root}/vqe_thetas.json"
    if not os.path.isfile(th_path):
        print(f"ERROR: input not found: {th_path}", file=sys.stderr)
        raise SystemExit(2)
    with open(th_path) as f:
        store = json.load(f)
    # 获胜条目：best_fun 配 best_x（含钳位；兼容 best_fun/best 键名）
    points = {}
    for key, rec in store.items():
        delta, s, init = key.split("|")
        bx = rec.get("best_x")
        if bx is None:  # 旧格式回落：raw 最小（仅 task3 链首，无钳位）
            win = min(rec["seeds"], key=lambda d: d["fun"])
            bx, bf = win["x"], win["fun"]
        else:
            bf = rec.get("best_fun", rec["best"])
        assert len(bx) == 4 * k, (key, len(bx), k)
        points.setdefault((float(delta), float(s)), []).append((bf, init, bx))
    q_rows, z_rows = [], []
    for (delta, s), cands in sorted(points.items()):
        fun, init, x = min(cands, key=lambda t: t[0])
        psi = statevector_of(build_vqe_circuit(init, x, n_layers=k))
        q, _, _ = Q_of_state(psi)
        tilde, _, _, _ = tilde_ZR_of_state(psi)
        q_rows.append((s, delta, q))
        z_rows.append((s, delta, tilde))
    with open(f"{root}/vqe_Q_L8_OBC.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "Q_vqe"])
        for s, delta, q in q_rows:
            w.writerow([f"{s:.8f}", f"{delta:.8f}", f"{q:.10f}"])
    with open(f"{root}/vqe_ZR_L8_OBC.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "ZR_vqe"])
        for s, delta, z in z_rows:
            w.writerow([f"{s:.8f}", f"{delta:.8f}", f"{z:.10f}"])
    print(f"wrote {root}/vqe_Q_L8_OBC.csv + vqe_ZR_L8_OBC.csv ({len(q_rows)} rows)")


if __name__ == "__main__":
    main()

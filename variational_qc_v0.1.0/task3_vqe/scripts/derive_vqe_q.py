#!/usr/bin/env python
"""task3 VQE-Q 派生：从 thetas 存档逐点取获胜 (init,seed)，重建电路求 Q.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task3_vqe/scripts/derive_vqe_q.py [--out PATH]

纯后处理，不做优化。输出 s,delta,Q_vqe（102 行，delta 外层、s 内层）。
"""

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from ansatz import build_vqe_circuit, statevector_of
from observables import Q_of_state

INITS = ["triv", "topo", "afm"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--thetas", default="task3_vqe/data/interim/vqe_thetas.json")
    ap.add_argument("--out", default="task3_vqe/data/interim/vqe_Q_L8_OBC.csv")
    args = ap.parse_args()
    for p in (args.thetas,):
        if not os.path.isfile(p):
            print(f"ERROR: input not found: {p}", file=sys.stderr)
            raise SystemExit(2)
    with open(args.thetas) as f:
        store = json.load(f)
    # 按 (delta, s) 聚集，逐点在全部 (init, seed) 上 argmin
    points = {}
    for key, rec in store.items():
        delta, s, init = key.split("|")
        for sd in rec["seeds"]:
            points.setdefault((float(delta), float(s)), []).append(
                (sd["fun"], init, sd["x"])
            )
    rows = []
    for (delta, s), cands in sorted(points.items()):
        fun, init, x = min(cands, key=lambda t: t[0])
        psi = statevector_of(build_vqe_circuit(init, x))
        q, _, _ = Q_of_state(psi)
        rows.append((s, delta, q, init, fun))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "Q_vqe"])
        for s, delta, q, _, _ in rows:
            w.writerow([f"{s:.8f}", f"{delta:.8f}", f"{q:.10f}"])
    print(f"wrote {args.out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()

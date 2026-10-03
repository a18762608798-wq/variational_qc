#!/usr/bin/env python
"""task3 VQE-ZR 派生：从 thetas 存档逐点取获胜 (init,seed)，重建电路求 tilde_ZR.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task3_vqe/scripts/derive_vqe_zr.py [--out PATH]

纯后处理，不做优化。输出 s,delta,ZR_vqe（102 行，delta 外层、s 内层）。
"""

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from ansatz import build_vqe_circuit, statevector_of
from zr_obs import tilde_ZR_of_state


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--thetas", default="task3_vqe/data/interim/vqe_thetas.json")
    ap.add_argument("--out", default="task3_vqe/data/interim/vqe_ZR_L8_OBC.csv")
    args = ap.parse_args()
    if not os.path.isfile(args.thetas):
        print(f"ERROR: input not found: {args.thetas}", file=sys.stderr)
        raise SystemExit(2)
    with open(args.thetas) as f:
        store = json.load(f)
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
        tilde, _, _, _ = tilde_ZR_of_state(psi)
        rows.append((s, delta, tilde))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "ZR_vqe"])
        for s, delta, z in rows:
            w.writerow([f"{s:.8f}", f"{delta:.8f}", f"{z:.10f}"])
    print(f"wrote {args.out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()

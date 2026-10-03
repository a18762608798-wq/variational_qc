#!/usr/bin/env python
"""task5 Q/ZR/P 派生：获胜 thetas 重建电路，求 Q、tilde_ZR 与 P 期望.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task5_vqe_nosym/scripts/derive_nosym_qzr.py --depth K

纯后处理，不做优化。输出 depthK/data/interim/vqe_Q_L8_OBC.csv、
vqe_ZR_L8_OBC.csv、vqe_P_diag.csv（各 102 行）。P 期望只记录不断言。
"""

import argparse
import csv
import json
import os
import sys

_HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)  # task5 ansatz（nosym 初态 + n_layers）优先
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(_HERE)),
                                "task3_vqe", "scripts"))  # observables/zr_obs 复用

from ansatz import P_matrix, build_vqe_circuit, statevector_of  # noqa: E402 task5 版
from observables import Q_of_state  # noqa: E402
from zr_obs import tilde_ZR_of_state  # noqa: E402

assert "nosym" in open(os.path.join(_HERE, "ansatz.py")).read()

LAYERS = {1: 1, 5: 5}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, required=True, choices=[1, 5])
    args = ap.parse_args()
    k = args.depth
    n = LAYERS[k]
    root = f"task5_vqe_nosym/depth{k}/data/interim"
    th_path = f"{root}/vqe_thetas.json"
    if not os.path.isfile(th_path):
        print(f"ERROR: input not found: {th_path}", file=sys.stderr)
        raise SystemExit(2)
    with open(th_path) as f:
        store = json.load(f)
    P = P_matrix()
    points = {}
    for key, rec in store.items():
        delta, s, init = key.split("|")
        bx = rec.get("best_x")
        if bx is None:
            win = min(rec["seeds"], key=lambda d: d["fun"])
            bx, bf = win["x"], win["fun"]
        else:
            bf = rec.get("best_fun", rec["best"])
        assert len(bx) == 4 * n, (key, len(bx), n)
        points.setdefault((float(delta), float(s)), []).append((bf, init, bx))
    q_rows, z_rows, p_rows = [], [], []
    for (delta, s), cands in sorted(points.items()):
        fun, init, x = min(cands, key=lambda t: t[0])
        psi = statevector_of(build_vqe_circuit(init, x, n_layers=n))
        q, _, _ = Q_of_state(psi)
        tilde, _, _, _ = tilde_ZR_of_state(psi)
        import numpy as np
        pexp = float(np.real(np.vdot(psi, P @ psi)))
        q_rows.append((s, delta, q))
        z_rows.append((s, delta, tilde))
        p_rows.append((s, delta, init, pexp))
    for name, rows, head in [("vqe_Q_L8_OBC.csv", q_rows, ["s", "delta", "Q_vqe"]),
                             ("vqe_ZR_L8_OBC.csv", z_rows, ["s", "delta", "ZR_vqe"])]:
        with open(f"{root}/{name}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            for s, delta, v in rows:
                w.writerow([f"{s:.8f}", f"{delta:.8f}", f"{v:.10f}"])
    with open(f"{root}/vqe_P_diag.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "init", "P_exp"])
        for s, delta, init, p in p_rows:
            w.writerow([f"{s:.8f}", f"{delta:.8f}", init, f"{p:.10f}"])
    print(f"wrote {root}/vqe_Q/ZR/P CSVs ({len(q_rows)} rows)")


if __name__ == "__main__":
    main()

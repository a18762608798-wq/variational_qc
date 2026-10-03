#!/usr/bin/env python
"""task10 orbit 逐深度 Q/ZR 派生：获胜 thetas 重建 orbit 电路，求 Q 与 tilde_ZR.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task10_reflect_orbit/scripts/derive_orbit_qzr.py --depth K

纯后处理，不做优化。输出 depthK/data/interim/vqe_Q_L8_OBC.csv 与
vqe_ZR_L8_OBC.csv（各 102 行，s,delta + 值列）。算子复用 task3 实现
（observables.Q_of_state、zr_obs.tilde_ZR_of_state），不重实现。
"""

import argparse
import csv
import json
import os
import sys

_HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)  # task10 orbit ansatz 优先
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(_HERE)),
                                "task3_vqe", "scripts"))  # observables/zr_obs 复用

from ansatz_orbit import build_vqe_circuit, statevector_of  # noqa: E402  orbit 版
from observables import Q_of_state  # noqa: E402
from zr_obs import tilde_ZR_of_state  # noqa: E402

import ansatz_orbit as _ax  # noqa: E402,F401  确认 orbit 版（含 O_GROUPS）

assert hasattr(_ax, "O_GROUPS") and hasattr(_ax, "E_GROUPS")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--thetas", default=None)
    ap.add_argument("--q-out", default=None)
    ap.add_argument("--zr-out", default=None)
    args = ap.parse_args()
    k = args.depth
    root = f"task10_reflect_orbit/depth{k}/data/interim"
    th_path = args.thetas or f"{root}/vqe_thetas.json"
    q_path = args.q_out or f"{root}/vqe_Q_L8_OBC.csv"
    zr_path = args.zr_out or f"{root}/vqe_ZR_L8_OBC.csv"
    if not os.path.isfile(th_path):
        print(f"ERROR: input not found: {th_path}", file=sys.stderr)
        raise SystemExit(2)
    with open(th_path) as f:
        store = json.load(f)
    # 获胜条目：best_fun 配 best_x（含钳位；兼容 seeds-only 格式如 depth1）
    points = {}
    for key, rec in store.items():
        delta, s, init = key.split("|")
        bx = rec.get("best_x")
        if bx is None:
            win = min(rec["seeds"], key=lambda d: d["fun"])
            bx, bf = win["x"], win["fun"]
        else:
            bf = rec.get("best_fun", rec["best"])
        assert len(bx) == 8 * k, (key, len(bx), k)
        points.setdefault((float(delta), float(s)), []).append((bf, init, bx))
    q_rows, z_rows = [], []
    for (delta, s), cands in sorted(points.items()):
        fun, init, x = min(cands, key=lambda t: t[0])
        psi = statevector_of(build_vqe_circuit(init, x, n_layers=k))
        q, _, _ = Q_of_state(psi)
        tilde, _, _, _ = tilde_ZR_of_state(psi)
        q_rows.append((s, delta, q))
        z_rows.append((s, delta, tilde))
    assert len(q_rows) == 102, f"expected 102 points, got {len(q_rows)}"
    for path, rows, col in ((q_path, q_rows, "Q_vqe"), (zr_path, z_rows, "ZR_vqe")):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["s", "delta", col])
            for s, delta, v in rows:
                w.writerow([f"{s:.8f}", f"{delta:.8f}", f"{v:.10f}"])
    print(f"wrote {q_path} + {zr_path} ({len(q_rows)} rows each)")


if __name__ == "__main__":
    main()

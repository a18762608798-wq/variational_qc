#!/usr/bin/env python
"""task5 depth5 直跳全量：depth1 nosym 最优 +16 参数微扰 -> depth5.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task5_vqe_nosym/scripts/sweep_d5.py [--workers N]

2 δ x 51 s x 3 初态 x 3 微扰取最优，深层以下不差于垫底。输出
depth5/data/interim/vqe_L8_OBC.csv（102 行）+ vqe_thetas.json。
增量 ckpt；任一格点失败非零退出且不写 CSV。
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import csv
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy.optimize import minimize

from ansatz import build_vqe_circuit, statevector_of, expectation, H_matrix

DELTAS = [-1.0, 1.0]
NS = 51
INITS = ["triv", "topo", "afm"]
SEED_BASE = 20260923
N_RESTARTS = 3
PERTURB_SCALE = 0.4
COBYLA_MAXITER = 500
N_LAYERS = 5
D1_THETAS = "task5_vqe_nosym/depth1/data/interim/vqe_thetas.json"


def _one(job):
    import numpy as np
    from scipy.optimize import minimize

    from ansatz import build_vqe_circuit, statevector_of, expectation, H_matrix

    s, delta, init, base_x, base_fun = job
    H = H_matrix(s, delta)

    def fun(theta):
        return expectation(statevector_of(build_vqe_circuit(init, theta, n_layers=5)), H)

    seeds = []
    for restart in range(N_RESTARTS):
        rng = np.random.default_rng(
            hash((SEED_BASE, 5, round(s, 8), round(delta, 8), init, restart)) % (2**31))
        x0 = np.concatenate([np.asarray(base_x), rng.uniform(-PERTURB_SCALE, PERTURB_SCALE, 16)])
        loc = minimize(fun, x0=x0, method="COBYLA",
                       options={"maxiter": COBYLA_MAXITER})
        seeds.append({"restart": restart,
                      "x": [float(v) for v in np.asarray(loc.x).ravel()],
                      "fun": float(loc.fun)})
    win = min(seeds, key=lambda d: d["fun"])
    if win["fun"] <= base_fun:
        best_x, best_fun = win["x"], win["fun"]
    else:
        best_x, best_fun = list(base_x) + [0.0] * 16, base_fun
    return {"s": s, "delta": delta, "init": init, "best": best_fun,
            "best_x": best_x, "seeds": seeds}


def _key(s, delta, init):
    return f"{delta}|{s}|{init}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if not os.path.isfile(D1_THETAS):
        print(f"ERROR: need depth1 thetas first: {D1_THETAS}", file=sys.stderr)
        raise SystemExit(2)
    with open(D1_THETAS) as f:
        prev = json.load(f)
    root = "task5_vqe_nosym/depth5/data/interim"
    out_csv, out_th, ckpt = f"{root}/vqe_L8_OBC.csv", f"{root}/vqe_thetas.json", f"{root}/sweep_ckpt.json"
    ss = [round(float(x), 8) for x in np.linspace(0.0, 1.0, NS)]
    jobs = []
    for d in DELTAS:
        for s in ss:
            for i in INITS:
                rec = prev[f"{d}|{s}|{i}"]
                win = min(rec["seeds"], key=lambda sd: sd["fun"])
                jobs.append((s, d, i, win["x"], win["fun"]))
    store = {}
    if os.path.isfile(ckpt):
        with open(ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {ckpt}", flush=True)
    todo = [j for j in jobs if _key(j[0], j[1], j[2]) not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(_one, todo):
            store[_key(r["s"], r["delta"], r["init"])] = r
            with open(ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 10 == 0 or len(store) == len(jobs):
                print(f"... depth5: {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
    assert len(store) == len(jobs), "missing results; refusing to write"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "E_triv", "E_topo", "E_afm"])
        for d in DELTAS:
            for s in ss:
                w.writerow([s, d] + [f"{store[_key(s, d, i)]['best']:.10f}" for i in INITS])
    with open(out_th, "w") as f:
        json.dump(store, f)
    print(f"wrote {out_csv} + {out_th} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

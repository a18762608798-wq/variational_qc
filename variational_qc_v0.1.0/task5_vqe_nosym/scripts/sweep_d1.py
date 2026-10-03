#!/usr/bin/env python
"""task5 depth1 全局扫描：nosym 初态 x task3 同形两步优化（DE 全局 + COBYLA polish）.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task5_vqe_nosym/scripts/sweep_d1.py [--workers N]

2 δ x 51 s x 3 初态 x 3 seed 取最优。输出 depth1/data/interim/vqe_L8_OBC.csv
（102 行）+ vqe_thetas.json。增量 ckpt；任一格点失败非零退出且不写 CSV。
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
from scipy.optimize import differential_evolution, minimize

from ansatz import H_matrix, build_vqe_circuit, statevector_of, expectation

DELTAS = [-1.0, 1.0]
NS = 51
INITS = ["triv", "topo", "afm"]
SEED_BASE = 20260923
N_SEEDS = 3
BOUNDS = [(0.0, 2 * np.pi)] * 4
BUDGET = {"de_maxiter": 30, "de_popsize": 10, "cobyla_maxiter": 300}


def derive_seed(s, delta, init, restart):
    return hash((SEED_BASE, round(float(s), 8), round(float(delta), 8),
                 init, int(restart))) % (2**31)


def _one(job):
    import numpy as np
    from scipy.optimize import differential_evolution, minimize

    from ansatz import H_matrix, build_vqe_circuit, statevector_of, expectation

    s, delta, init = job
    H = H_matrix(s, delta)

    def fun(theta):
        return expectation(statevector_of(build_vqe_circuit(init, theta, n_layers=1)), H)

    seeds = []
    for restart in range(N_SEEDS):
        de = differential_evolution(fun, bounds=BOUNDS, maxiter=BUDGET["de_maxiter"],
                                    popsize=BUDGET["de_popsize"],
                                    seed=derive_seed(s, delta, init, restart),
                                    polish=False, updating="deferred", workers=1)
        loc = minimize(fun, x0=np.asarray(de.x), method="COBYLA",
                       options={"maxiter": BUDGET["cobyla_maxiter"]})
        seeds.append({"restart": restart,
                      "x": [float(v) for v in np.asarray(loc.x).ravel()],
                      "fun": float(loc.fun), "global_fun": float(de.fun)})
    best = min(seeds, key=lambda d: d["fun"])
    return {"s": s, "delta": delta, "init": init, "best": best["fun"],
            "best_x": best["x"], "seeds": seeds}


def _key(s, delta, init):
    return f"{delta}|{s}|{init}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    root = "task5_vqe_nosym/depth1/data/interim"
    out_csv, out_th, ckpt = f"{root}/vqe_L8_OBC.csv", f"{root}/vqe_thetas.json", f"{root}/sweep_ckpt.json"
    ss = [round(float(x), 8) for x in np.linspace(0.0, 1.0, NS)]
    jobs = [(s, d, i) for d in DELTAS for s in ss for i in INITS]
    store = {}
    if os.path.isfile(ckpt):
        with open(ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {ckpt}", flush=True)
    todo = [j for j in jobs if _key(*j) not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(_one, todo):
            store[_key(r["s"], r["delta"], r["init"])] = r
            with open(ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 10 == 0 or len(store) == len(jobs):
                print(f"... depth1: {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
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

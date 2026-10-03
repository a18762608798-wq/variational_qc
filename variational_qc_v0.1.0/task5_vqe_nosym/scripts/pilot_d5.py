#!/usr/bin/env python
"""task5 depth5 直跳 pilot：depth1 nosym 最优 +16 参数微扰 -> depth5.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task5_vqe_nosym/scripts/pilot_d5.py [--workers N]

pilot 点：delta=+1 上 s in {0.0, 0.5, 0.98} x 三初态；微扰尺度 {0.2, 0.4, 0.6}
x 2 restart。输出 config/pilot.csv（含 L1 基准与 L5 结果）。增量 ckpt。
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

PILOT_S = [0.0, 0.5, 0.98]
PILOT_DELTA = 1.0
INITS = ["triv", "topo", "afm"]
SCALES = [0.2, 0.4, 0.6]
RESTARTS = [0, 1]
SEED_BASE = 20260923
COBYLA_MAXITER = 500
D1_THETAS = "task5_vqe_nosym/depth1/data/interim/vqe_thetas.json"


def _one(job):
    import numpy as np
    from scipy.optimize import minimize

    from ansatz import H_matrix, build_vqe_circuit, statevector_of, expectation

    s, delta, init, scale, restart = job
    with open(D1_THETAS) as f:
        base = min(json.load(f)[f"{delta}|{s}|{init}"]["seeds"],
                   key=lambda d: d["fun"])
    H = H_matrix(s, delta)

    def fun(theta):
        return expectation(statevector_of(build_vqe_circuit(init, theta, n_layers=5)), H)

    rng = np.random.default_rng(
        hash((SEED_BASE, 5, round(s, 8), round(delta, 8), init, restart)) % (2**31))
    x0 = np.concatenate([np.asarray(base["x"]), rng.uniform(-scale, scale, 16)])
    t = time.time()
    loc = minimize(fun, x0=x0, method="COBYLA",
                   options={"maxiter": COBYLA_MAXITER})
    dt = time.time() - t
    pf = float(loc.fun)
    if pf > base["fun"]:
        return (s, delta, init, scale, restart, base["fun"], base["fun"], dt)
    return (s, delta, init, scale, restart, base["fun"], pf, dt)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="task5_vqe_nosym/config/pilot.csv")
    ap.add_argument("--ckpt", default="task5_vqe_nosym/config/pilot_ckpt.json")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if not os.path.isfile(D1_THETAS):
        print(f"ERROR: need depth1 thetas first: {D1_THETAS}", file=sys.stderr)
        raise SystemExit(2)
    jobs = [(s, PILOT_DELTA, i, sc, r)
            for s in PILOT_S for i in INITS for sc in SCALES for r in RESTARTS]
    store = {}
    if os.path.isfile(args.ckpt):
        with open(args.ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {args.ckpt}", flush=True)
    todo = [j for j in jobs if "|".join(map(str, j)) not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for s, d, i, sc, r, b, pf, dt in ex.map(_one, todo):
            store["|".join(map(str, (s, d, i, sc, r)))] = (b, pf, dt)
            with open(args.ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 6 == 0 or len(store) == len(jobs):
                print(f"... {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
    assert len(store) == len(jobs)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "init", "scale", "restart", "L1", "L5", "time_s"])
        for key in sorted(store):
            s, d, i, sc, r = key.split("|")
            b, pf, dt = store[key]
            w.writerow([s, d, i, sc, r, f"{b:.10f}", f"{pf:.10f}", f"{dt:.0f}"])
    print(f"wrote {args.out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""task10 orbit pilot：depth1 代表性点两档预算 + depth2 微扰尺度探针.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task10_reflect_orbit/scripts/pilot_orbit.py [--out PATH] [--workers N]

pilot 点：delta=+1 上 s in {0.0, 0.5, 0.98} x 三初态 x 3 seed x 两档预算
（light: de_maxiter=30/popsize=15/cobyla=300；base: 50/20/500）。
depth2 探针：每 (s,init) 取 light 最优 seed 为垫底，微扰尺度 {0.1, 0.3} x 2 restart。
输出 pilot.csv + pilot_warm.csv，供 config/pilot.md 定全量预算。
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

PILOT_S = [0.0, 0.5, 0.98]
PILOT_DELTA = 1.0
INITS = ["triv", "topo", "afm"]
SEEDS = [0, 1, 2]
BUDGETS = {
    "light": {"de_maxiter": 30, "de_popsize": 15, "cobyla_maxiter": 300},
    "base": {"de_maxiter": 50, "de_popsize": 20, "cobyla_maxiter": 500},
}
SEED_BASE = 20260929
SCALES = [0.1, 0.3]
WARM_RESTARTS = [0, 1]
WARM_MAXITER = 500


def _one_d1(job):
    import numpy as np

    from ansatz_orbit import H_matrix
    from optimize_orbit import two_step, derive_seed_d1

    s, delta, init, seed, blabel, budget = job
    H = H_matrix(s, delta)
    t = time.time()
    r = two_step(init, H, derive_seed_d1(SEED_BASE, s, delta, init, seed),
                 budget, n_layers=1)
    dt = time.time() - t
    return (s, delta, init, seed, blabel, r["global_fun"], r["fun"],
            [float(v) for v in np.asarray(r["x"]).ravel()], dt)


def _one_warm(job):
    from ansatz_orbit import H_matrix
    from optimize_orbit import derive_seed, warm_start

    s, delta, init, base_x, base_fun, scale, restart = job
    H = H_matrix(s, delta)
    t = time.time()
    r = warm_start(init, H, 2, base_x,
                   derive_seed(SEED_BASE, 2, s, delta, init, restart),
                   perturb_scale=scale, cobyla_maxiter=WARM_MAXITER)
    dt = time.time() - t
    if r["fun"] > base_fun:
        fun = base_fun  # 钳位回垫底（与全量语义一致）
    else:
        fun = r["fun"]
    return (s, delta, init, scale, restart, base_fun, fun, dt)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="task10_reflect_orbit/config/pilot.csv")
    ap.add_argument("--warm-out", default="task10_reflect_orbit/config/pilot_warm.csv")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    jobs = [
        (s, PILOT_DELTA, init, seed, blabel, budget)
        for s in PILOT_S
        for init in INITS
        for seed in SEEDS
        for blabel, budget in BUDGETS.items()
    ]
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    d1res = {}
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "init", "seed", "budget", "global_fun", "fun", "time_s"])
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for s, delta, init, seed, blabel, gf, pf, x, dt in ex.map(_one_d1, jobs):
                w.writerow([s, delta, init, seed, blabel,
                            f"{gf:.10f}", f"{pf:.10f}", f"{dt:.1f}"])
                f.flush()
                d1res[(s, delta, init, seed, blabel)] = (pf, x)
                print(f"s={s} {init} seed={seed} {blabel}: "
                      f"global={gf:.6f} polished={pf:.6f} ({dt:.0f}s)", flush=True)
    print(f"wrote {args.out}")
    # depth2 探针：每 (s,init) 取 light 最优 seed 垫底
    wjobs = []
    for s in PILOT_S:
        for init in INITS:
            cands = [(d1res[(s, PILOT_DELTA, init, sd, "light")][0], sd) for sd in SEEDS]
            _, best_seed = min(cands)
            base_fun, base_x = d1res[(s, PILOT_DELTA, init, best_seed, "light")]
            for sc in SCALES:
                for r in WARM_RESTARTS:
                    wjobs.append((s, PILOT_DELTA, init, base_x, base_fun, sc, r))
    with open(args.warm_out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "init", "scale", "restart", "L1", "L2", "time_s"])
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for s, delta, init, sc, r, l1, l2, dt in ex.map(_one_warm, wjobs):
                w.writerow([s, delta, init, sc, r, f"{l1:.10f}", f"{l2:.10f}", f"{dt:.1f}"])
                f.flush()
                print(f"warm s={s} {init} scale={sc} restart={r}: "
                      f"L1={l1:.6f} L2={l2:.6f} ({dt:.0f}s)", flush=True)
    print(f"wrote {args.warm_out}")


if __name__ == "__main__":
    main()

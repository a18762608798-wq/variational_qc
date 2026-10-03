#!/usr/bin/env python
"""task3 pilot：代表性 s 点 x 三初态 x 多 seed x 两档预算，输出收敛结论.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task3_vqe/scripts/pilot.py [--out PATH]

输出 CSV（s,delta,init,seed,budget,global_fun,fun,time_s），供分析定全量预算。
pilot 点：delta=+1 上 s in {0.0, 0.5, 0.98}（深平庸端、过渡区、简并区）。
"""

import argparse
import csv
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from ansatz import H_matrix
from optimize import two_step, derive_seed

PILOT_S = [0.0, 0.5, 0.98]
PILOT_DELTA = 1.0
INITS = ["triv", "topo", "afm"]
SEEDS = [0, 1, 2]
BUDGETS = {
    "light": {"de_maxiter": 30, "de_popsize": 10, "cobyla_maxiter": 300},
    "base": {"de_maxiter": 50, "de_popsize": 10, "cobyla_maxiter": 500},
}
SEED_BASE = 20260921


def _one(job):
    # 每个 worker 限单线程，避免 BLAS 超订（需在 import numpy 前生效则更好，
    # 此处进程已起，仅作软约束；主要并行度来自进程数）。
    import numpy as np

    from ansatz import H_matrix
    from optimize import two_step, derive_seed

    s, delta, init, seed, blabel, budget = job
    H = H_matrix(s, delta)
    t = time.time()
    r = two_step(init, H, derive_seed(SEED_BASE, s, delta, init, seed), budget)
    dt = time.time() - t
    return (s, delta, init, seed, blabel, r["global_fun"], r["fun"], dt)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="task3_vqe/data/interim/pilot.csv")
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
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "init", "seed", "budget", "global_fun", "fun", "time_s"])
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for s, delta, init, seed, blabel, gf, pf, dt in ex.map(_one, jobs):
                w.writerow([s, delta, init, seed, blabel, f"{gf:.10f}", f"{pf:.10f}", f"{dt:.1f}"])
                f.flush()
                print(f"s={s} {init} seed={seed} {blabel}: "
                      f"global={gf:.6f} polished={pf:.6f} ({dt:.0f}s)", flush=True)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

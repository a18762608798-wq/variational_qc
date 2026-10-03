#!/usr/bin/env python
"""task3 全量扫描：2 delta x 51 s x 3 初态 x 3 seed 取最优 -> vqe_L8_OBC.csv.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task3_vqe/scripts/sweep.py [--workers N]

预算与 seed 数见 task3_vqe/config/grid.toml（pilot 锁定）。任一格点失败则
非零退出且不写 CSV（不得静默填数）。输出 102 行，delta 外层、s 内层。

中间产物（增量 checkpoint，每完成一格点即落盘，可 resume）：
- task3_vqe/data/interim/sweep_ckpt.json：逐格点全部 seed 的 theta 与目标值
- 最终附带 task3_vqe/data/interim/vqe_thetas.json：同上全量，供后续复用
  （warm start、多层初始化、优化轨迹分析）
"""

# 线程钉死必须在 numpy/scipy import 之前（见 pilot.md 结论 6）
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

DELTAS = [-1.0, 1.0]
NS = 51
INITS = ["triv", "topo", "afm"]
SEED_BASE = 20260921
N_SEEDS = 3
BUDGET = {"de_maxiter": 30, "de_popsize": 10, "cobyla_maxiter": 300}


def _one(job):
    import numpy as np

    from ansatz import H_matrix
    from optimize import two_step, derive_seed

    s, delta, init = job
    H = H_matrix(s, delta)
    seeds = []
    for restart in range(N_SEEDS):
        r = two_step(init, H, derive_seed(SEED_BASE, s, delta, init, restart), BUDGET)
        seeds.append(
            {
                "restart": restart,
                "x": [float(v) for v in np.asarray(r["x"]).ravel()],
                "fun": float(r["fun"]),
                "global_fun": float(r["global_fun"]),
            }
        )
    best = min(seeds, key=lambda d: d["fun"])
    return {"s": s, "delta": delta, "init": init, "best": best["fun"], "seeds": seeds}


def _key(s, delta, init):
    return f"{delta}|{s}|{init}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default="task3_vqe/data/interim/vqe_L8_OBC.csv")
    ap.add_argument("--thetas", default="task3_vqe/data/interim/vqe_thetas.json")
    ap.add_argument("--ckpt", default="task3_vqe/data/interim/sweep_ckpt.json")
    args = ap.parse_args()
    ss = [round(float(x), 8) for x in np.linspace(0.0, 1.0, NS)]
    jobs = [(s, d, i) for d in DELTAS for s in ss for i in INITS]

    store = {}
    if os.path.isfile(args.ckpt):
        with open(args.ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {args.ckpt}", flush=True)
    todo = [j for j in jobs if _key(*j) not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(_one, todo):
            store[_key(r["s"], r["delta"], r["init"])] = r
            with open(args.ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 10 == 0 or len(store) == len(jobs):
                print(f"... {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
    # 任一缺失即失败（map 本身会抛 worker 异常）
    assert len(store) == len(jobs), "missing results; refusing to write"
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "E_triv", "E_topo", "E_afm"])
        for d in DELTAS:
            for s in ss:
                w.writerow([s, d] + [f"{store[_key(s, d, i)]['best']:.10f}" for i in INITS])
    with open(args.thetas, "w") as f:
        json.dump(store, f)
    print(f"wrote {args.out} ({len(jobs) // 3} rows) + {args.thetas} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

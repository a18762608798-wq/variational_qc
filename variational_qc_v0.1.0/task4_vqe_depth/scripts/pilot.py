#!/usr/bin/env python
"""task4 pilot：逐点 L1->L2->L3->L4->L5 warm-start 链，测微扰尺度与增益.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task4_vqe_depth/scripts/pilot.py [--out PATH] [--workers N]

pilot 点：delta=+1 上 s in {0.0, 0.5, 0.98} x 三初态；微扰尺度 {0.1, 0.3} x 2 restart。
每条链：task3 L1 获胜 theta 出发，逐层 warm-start，记录每层 fun。增量 ckpt，可 resume。
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
SCALES = [0.1, 0.3]
RESTARTS = [0, 1]
SEED_BASE = 20260922
COBYLA_MAXITER = 500
TASK3_THETAS = "task3_vqe/data/interim/vqe_thetas.json"


def _one(job):
    import json as _json

    from ansatz import H_matrix
    from optimize import derive_seed, warm_start

    s, delta, init, scale, restart = job
    with open(TASK3_THETAS) as f:
        store = _json.load(f)
    rec = store[f"{delta}|{s}|{init}"]
    base = min(rec["seeds"], key=lambda d: d["fun"])
    H = H_matrix(s, delta)
    out = {"s": s, "delta": delta, "init": init, "scale": scale,
           "restart": restart, "L1": base["fun"], "chain": []}
    theta = base["x"]
    t = time.time()
    for depth in (2, 3, 4, 5):
        r = warm_start(init, H, depth, theta,
                       derive_seed(SEED_BASE, depth, s, delta, init, restart),
                       perturb_scale=scale, cobyla_maxiter=COBYLA_MAXITER)
        # 深层以下不差于垫底（零微扰即浅层最优）
        if r["fun"] > base["fun"]:
            r = {"x": list(theta) + [0.0, 0.0, 0.0, 0.0], "fun": base["fun"]}
            theta = r["x"]
        else:
            theta = r["x"]
        base = {"fun": r["fun"]}
        out["chain"].append({"depth": depth, "fun": r["fun"]})
    out["time_s"] = time.time() - t
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="task4_vqe_depth/config/pilot.csv")
    ap.add_argument("--ckpt", default="task4_vqe_depth/config/pilot_ckpt.json")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    jobs = [(s, PILOT_DELTA, i, sc, r)
            for s in PILOT_S for i in INITS for sc in SCALES for r in RESTARTS]
    store = {}
    if os.path.isfile(args.ckpt):
        with open(args.ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {args.ckpt}", flush=True)
    todo = [j for j in jobs
            if f"{j[0]}|{j[1]}|{j[2]}|{j[3]}|{j[4]}" not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(_one, todo):
            store[f"{r['s']}|{r['delta']}|{r['init']}|{r['scale']}|{r['restart']}"] = r
            with open(args.ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 6 == 0 or len(store) == len(jobs):
                print(f"... {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
    assert len(store) == len(jobs)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "init", "scale", "restart", "L1",
                    "L2", "L3", "L4", "L5", "time_s"])
        for key in sorted(store, key=lambda k: tuple(float(x) if j < 2 else x
                           for j, x in enumerate(k.split("|")))):
            r = store[key]
            w.writerow([r["s"], r["delta"], r["init"], r["scale"], r["restart"],
                        f"{r['L1']:.10f}"] +
                       [f"{c['fun']:.10f}" for c in r["chain"]] +
                       [f"{r['time_s']:.0f}"])
    print(f"wrote {args.out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

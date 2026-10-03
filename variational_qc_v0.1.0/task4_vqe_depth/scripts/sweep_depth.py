#!/usr/bin/env python
"""task4 逐深度全量扫描：depth k 由 depth k-1 thetas 逐点 warm-start.

用法（仓库根目录，深度串行，k=2..5）：
    .CondaPkg/.pixi/envs/default/bin/python -u task4_vqe_depth/scripts/sweep_depth.py --depth K [--workers N]

depth2 由 task3 thetas 递推；每点 3 restart 取最优，深层以下不差于垫底。
输出 depthK/data/interim/vqe_L8_OBC.csv（102 行）+ vqe_thetas.json。
增量 ckpt（abort-safe）；任一格点失败非零退出且不写 CSV。
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

DELTAS = [-1.0, 1.0]
NS = 51
INITS = ["triv", "topo", "afm"]
SEED_BASE = 20260922
N_RESTARTS = 3
PERTURB_SCALE = 0.3
COBYLA_MAXITER = 500


def _one(job):
    import numpy as np

    from ansatz import H_matrix
    from optimize import derive_seed, warm_start

    s, delta, init, depth, base_x, base_fun = job
    H = H_matrix(s, delta)
    seeds = []
    for restart in range(N_RESTARTS):
        r = warm_start(init, H, depth, base_x,
                       derive_seed(SEED_BASE, depth, s, delta, init, restart),
                       perturb_scale=PERTURB_SCALE, cobyla_maxiter=COBYLA_MAXITER)
        seeds.append({"restart": restart,
                      "x": [float(v) for v in np.asarray(r["x"]).ravel()],
                      "fun": float(r["fun"])})
    win = min(seeds, key=lambda d: d["fun"])
    # 深层以下不差于垫底：floor 取自上一深度 CSV 最优（含其实现 x），逐代单调
    if win["fun"] <= base_fun:
        best_x, best_fun = win["x"], win["fun"]
    else:
        best_x, best_fun = list(base_x) + [0.0] * 4, base_fun
    return {"s": s, "delta": delta, "init": init, "best": best_fun,
            "best_x": best_x, "seeds": seeds}


def _key(s, delta, init):
    return f"{delta}|{s}|{init}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    k = args.depth
    assert k >= 2
    root = f"task4_vqe_depth/depth{k}/data/interim"
    out_csv = f"{root}/vqe_L8_OBC.csv"
    out_th = f"{root}/vqe_thetas.json"
    ckpt = f"{root}/sweep_ckpt.json"
    prev_th = ("task3_vqe/data/interim/vqe_thetas.json" if k == 2
               else f"task4_vqe_depth/depth{k - 1}/data/interim/vqe_thetas.json")
    if not os.path.isfile(prev_th):
        print(f"ERROR: prev thetas not found: {prev_th}", file=sys.stderr)
        raise SystemExit(2)
    with open(prev_th) as f:
        prev = json.load(f)
    ss = [round(float(x), 8) for x in np.linspace(0.0, 1.0, NS)]
    jobs = []
    for d in DELTAS:
        for s in ss:
            for i in INITS:
                rec = prev[f"{d}|{s}|{i}"]
                if k == 2:
                    # task3 无钳位：CSV 最优即 raw 最小，直接取
                    win = min(rec["seeds"], key=lambda sd: sd["fun"])
                    jobs.append((s, d, i, k, win["x"], win["fun"]))
                    continue
                # base 取上一深度 CSV 最优及其实现 x（best_x），逐代单调；
                # 兼容 backfilled 旧键名 best_fun；缺键即失败，不静默回落
                jobs.append((s, d, i, k, rec["best_x"], rec.get("best_fun", rec["best"])))
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
                print(f"... depth{k}: {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
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

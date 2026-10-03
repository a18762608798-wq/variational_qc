#!/usr/bin/env python
"""task10 orbit 逐深度全量扫描.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python -u task10_reflect_orbit/scripts/sweep_orbit.py --depth K [--workers N]

- depth1：两步优化（DE 全局 + COBYLA polish），每点 n_seeds 取最优；
- depth>=2：由本任务 depth K-1 thetas 逐点 warm-start（垫底+微扰+polish，
  劣于垫底钳位回垫底），拒绝跨任务（uniform）thetas；
- 输出 depthK/data/interim/vqe_L8_OBC.csv（102 行）+ vqe_thetas.json；
- 增量 ckpt（abort-safe）；任一格点失败非零退出且不写 CSV。
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
SEED_BASE = 20260929
N_SEEDS = 3
BUDGET_D1 = {"de_maxiter": 30, "de_popsize": 15, "cobyla_maxiter": 300}
N_RESTARTS = 3
PERTURB_SCALE = 0.3
COBYLA_MAXITER_WARM = 500


def _check_prev_source(prev_th: str) -> None:
    bad_markers = ("task3", "task4", "task5", "uniform", "nosym")
    low = prev_th.lower()
    if any(m in low for m in bad_markers):
        raise SystemExit(
            f"ERROR: orbit sweep must chain from task10 depth K-1 thetas, "
            f"refusing cross-task source: {prev_th}")


def _one_d1(job):
    import numpy as np

    from ansatz_orbit import H_matrix
    from optimize_orbit import two_step, derive_seed_d1

    s, delta, init = job
    H = H_matrix(s, delta)
    seeds = []
    for restart in range(N_SEEDS):
        r = two_step(init, H, derive_seed_d1(SEED_BASE, s, delta, init, restart),
                     BUDGET_D1, n_layers=1)
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


def _one_warm(job):
    import numpy as np

    from ansatz_orbit import H_matrix
    from optimize_orbit import derive_seed, warm_start

    s, delta, init, depth, base_x, base_fun = job
    H = H_matrix(s, delta)
    seeds = []
    for restart in range(N_RESTARTS):
        r = warm_start(init, H, depth, base_x,
                       derive_seed(SEED_BASE, depth, s, delta, init, restart),
                       perturb_scale=PERTURB_SCALE, cobyla_maxiter=COBYLA_MAXITER_WARM)
        seeds.append({"restart": restart,
                      "x": [float(v) for v in np.asarray(r["x"]).ravel()],
                      "fun": float(r["fun"])})
    win = min(seeds, key=lambda d: d["fun"])
    # 深层以下不差于垫底：floor 取自上一深度 CSV 最优（含其实现 x），逐代单调
    if win["fun"] <= base_fun:
        best_x, best_fun = win["x"], win["fun"]
    else:
        best_x, best_fun = list(base_x) + [0.0] * 8, base_fun
    return {"s": s, "delta": delta, "init": init, "best": best_fun,
            "best_x": best_x, "seeds": seeds}


def _key(s, delta, init):
    return f"{delta}|{s}|{init}"


def _grid():
    return [round(float(x), 8) for x in np.linspace(0.0, 1.0, NS)]


def run_d1(root: str, out_csv: str, out_th: str, ckpt: str, workers: int) -> None:
    ss = _grid()
    jobs = [(s, d, i) for d in DELTAS for s in ss for i in INITS]
    store = {}
    if os.path.isfile(ckpt):
        with open(ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {ckpt}", flush=True)
    todo = [j for j in jobs if _key(*j) not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_one_d1, todo):
            store[_key(r["s"], r["delta"], r["init"])] = r
            with open(ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 10 == 0 or len(store) == len(jobs):
                print(f"... {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
    assert len(store) == len(jobs), "missing results; refusing to write"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "E_triv", "E_topo", "E_afm"])
        for d in DELTAS:
            for s in ss:
                w.writerow([s, d] + [f"{store[_key(s, d, i)]['best']:.10f}" for i in INITS])
    with open(out_th, "w") as f:
        json.dump(store, f)
    print(f"wrote {out_csv} ({len(jobs) // 3} rows) + {out_th} ({time.time() - t0:.0f}s)")


def run_warm(depth: int, root: str, out_csv: str, out_th: str, ckpt: str,
             prev_th: str, workers: int) -> None:
    _check_prev_source(prev_th)
    if not os.path.isfile(prev_th):
        print(f"ERROR: input not found: {prev_th}", file=sys.stderr)
        raise SystemExit(2)
    with open(prev_th) as f:
        prev = json.load(f)
    ss = _grid()
    jobs = []
    for d in DELTAS:
        for s in ss:
            for i in INITS:
                key = _key(s, d, i)
                if key not in prev:
                    print(f"ERROR: prev thetas missing key: {key}", file=sys.stderr)
                    raise SystemExit(2)
                rec = prev[key]
                if "best_x" in rec:
                    base_x, base_fun = rec["best_x"], rec.get("best_fun", rec["best"])
                else:
                    win = min(rec["seeds"], key=lambda dd: dd["fun"])
                    base_x, base_fun = win["x"], win["fun"]
                assert len(base_x) == 8 * (depth - 1), (
                    f"orbit warm-start dim mismatch at {key}: got {len(base_x)}, "
                    f"depth {depth} needs {8 * (depth - 1)} "
                    f"(uniform thetas must NOT be reused)")
                jobs.append((s, d, i, depth, base_x, base_fun))
    store = {}
    if os.path.isfile(ckpt):
        with open(ckpt) as f:
            store = json.load(f)
        print(f"resumed {len(store)}/{len(jobs)} from {ckpt}", flush=True)
    todo = [j for j in jobs if _key(j[0], j[1], j[2]) not in store]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_one_warm, todo):
            store[_key(r["s"], r["delta"], r["init"])] = r
            with open(ckpt, "w") as f:
                json.dump(store, f)
            if len(store) % 10 == 0 or len(store) == len(jobs):
                print(f"... {len(store)}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
    assert len(store) == len(jobs), "missing results; refusing to write"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "E_triv", "E_topo", "E_afm"])
        for d in DELTAS:
            for s in ss:
                w.writerow([s, d] + [f"{store[_key(s, d, i)]['best']:.10f}" for i in INITS])
    with open(out_th, "w") as f:
        json.dump(store, f)
    print(f"wrote {out_csv} ({len(jobs) // 3} rows) + {out_th} ({time.time() - t0:.0f}s)")


def main() -> None:
    ap = argparse.ArgumentParser(description="task10 orbit sweep (depth K).")
    ap.add_argument("--depth", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None)
    ap.add_argument("--thetas", default=None)
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--prev-thetas", default=None)
    args = ap.parse_args()
    k = args.depth
    root = f"task10_reflect_orbit/depth{k}/data/interim"
    out_csv = args.out or f"{root}/vqe_L8_OBC.csv"
    out_th = args.thetas or f"{root}/vqe_thetas.json"
    ckpt = args.ckpt or f"{root}/sweep_ckpt.json"
    if k == 1:
        run_d1(root, out_csv, out_th, ckpt, args.workers)
    else:
        prev_th = args.prev_thetas or (
            f"task10_reflect_orbit/depth{k - 1}/data/interim/vqe_thetas.json")
        run_warm(k, root, out_csv, out_th, ckpt, prev_th, args.workers)


if __name__ == "__main__":
    main()

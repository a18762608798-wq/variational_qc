#!/usr/bin/env python
"""task10 orbit 画布驱动：逐深度 x 逐 delta x 三类画布，共 18 组.

用法（仓库根目录）：
    .CondaPkg/.pixi/envs/default/bin/python task10_reflect_orbit/scripts/plot_orbit.py [--depth K] [--workers N]

每组调用 shared/viz/plot_vqe.py（复用既有渲染语言与 fail-closed/原子写语义）：
- min 模式：解析 E0/E1 + min(VQE-orbit) 三线；
- q 模式：解析 Q + Q_vqe-orbit 双线；
- zr 模式：解析 tilde_ZR + ZR_vqe-orbit 双线。
标题与文件名含 orbit 与深度标识；只写本任务 figures 目录，不碰 task3/4。
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLOT = os.path.join(ROOT, "shared", "viz", "plot_vqe.py")
PY = sys.executable

DEPTHS_ALL = [1, 2, 3]
DELTAS = [-1.0, 1.0]
DMAP = {-1.0: "deltam1", 1.0: "deltap1"}


def _names(depth: int, delta: float, mode: str) -> tuple[str, str]:
    dtag = DMAP[delta]
    base = {"min": "vqe_min_comparison", "q": "vqe_Q_comparison",
            "zr": "vqe_ZR_comparison"}[mode]
    png = (f"task10_reflect_orbit/depth{depth}/data/figures/"
           f"{base}_{dtag}_orbit_depth{depth}.png")
    title = {"min": f"VQE-orbit vs analytic (L=8, depth={depth}, delta={delta:g})",
             "q": f"Q-orbit vs analytic (L=8, depth={depth}, delta={delta:g})",
             "zr": f"ZR-orbit vs analytic (L=8, depth={depth}, delta={delta:g})"}[mode]
    return png, title


def one(depth: int, delta: float, mode: str) -> str:
    root = f"task10_reflect_orbit/depth{depth}/data/interim"
    png, title = _names(depth, delta, mode)
    cmd = [PY, PLOT, "--vqe-csv", f"{root}/vqe_L8_OBC.csv",
           "--spectra-csv", "task1_baseline/data/interim/spectra_L8_OBC.csv",
           "--q-vqe-csv", f"{root}/vqe_Q_L8_OBC.csv",
           "--q-csv", "task1_baseline/data/interim/Q_L8_OBC.csv",
           "--zr-vqe-csv", f"{root}/vqe_ZR_L8_OBC.csv",
           "--zr-csv", "task1_baseline/data/interim/tilde_ZR_L8_OBC.csv",
           "--delta", str(delta), "--mode", mode, "--png", png, "--title", title]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        raise SystemExit(r.returncode)
    return png


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=None, choices=[1, 2, 3])
    args = ap.parse_args()
    depths = [args.depth] if args.depth else list(DEPTHS_ALL)
    done = []
    for depth in depths:
        for delta in DELTAS:
            for mode in ("min", "q", "zr"):
                done.append(one(depth, delta, mode))
    print(f"wrote {len(done)} canvases")
    for p in done:
        print(" -", p)


if __name__ == "__main__":
    main()

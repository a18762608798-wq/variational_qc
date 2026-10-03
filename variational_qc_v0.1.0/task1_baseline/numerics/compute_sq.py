#!/usr/bin/env python
"""S(q) 曲线：从基态存档取三行做 Fourier 求和（OBC 格点标号约定见 doc/model/operator.md）。

取点：平庸 (s,delta)=(0,0)、SPT (1,0)、AFM 取 Spi CSV 实测峰值所在格点。
q 在 [0, 2pi] 密采样（OBC 下无量子化）。纯存档后处理，不碰求解。

用法：python src/numerics/compute_sq.py [--archive PATH] [--spi PATH]
    [--out PATH] [--nq INT]
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

L = 8
N = 2**L


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def zb(a: np.ndarray, j: int) -> np.ndarray:
    """格点 j（1-indexed，j=1 为 MSB）的 Z 本征值向量。"""
    return np.where(((a >> (L - j)) & 1) == 0, 1.0, -1.0)


def structure_factor(psi: np.ndarray, qs: np.ndarray) -> np.ndarray:
    p = np.abs(psi) ** 2
    a = np.arange(N)
    z = np.stack([zb(a, j) for j in range(1, L + 1)])  # (L, N)
    # C[i,j] = <Zi Zj>
    c = np.einsum("a,ia,ja->ij", p, z, z)
    ii, jj = np.mgrid[0:L, 0:L]
    # 注意：(-1)^{i-j} 只在 q=π 特例中出现（e^{iπ(i-j)}），通式 S(q) 不含此因子
    out = np.empty_like(qs, dtype=float)
    for k, q in enumerate(qs):
        out[k] = np.sum(np.cos(q * (ii - jj)) * c).real / L
    return out


def nearest_row(ss: np.ndarray, ds: np.ndarray, s: float, d: float) -> int:
    i = int(np.argmin(abs(ss - s)))
    j = int(np.argmin(abs(ds - d)))
    return j * len(ss) + i


def main() -> None:
    ap = argparse.ArgumentParser(description="S(q) curves for three representative states.")
    ap.add_argument("--archive", default="task1_baseline/data/interim/psi_archive.npz")
    ap.add_argument("--spi", default="task1_baseline/data/interim/Spi_L8_OBC.csv")
    ap.add_argument("--out", default="task1_baseline/data/interim/Sq_curves.csv")
    ap.add_argument("--nq", type=int, default=201)
    args = ap.parse_args()

    if not os.path.isfile(args.archive):
        fail(f"archive not found: {args.archive}")
    if not os.path.isfile(args.spi):
        fail(f"Spi CSV not found: {args.spi}")
    d = np.load(args.archive)
    psi, ss, ds = d["psi"], d["s_grid"], d["delta_grid"]
    if psi.shape[1] != N:
        fail(f"unexpected psi shape {psi.shape}, need (*, {N})")

    spi = pd.read_csv(args.spi)
    peak = spi.loc[spi["S_pi"].idxmax()]

    rows = {
        "S_trivial": nearest_row(ss, ds, 0.0, 0.0),
        "S_spt": nearest_row(ss, ds, 1.0, 0.0),
        "S_afm": nearest_row(ss, ds, float(peak["s"]), float(peak["delta"])),
    }
    pts = pd.DataFrame(
        {
            "curve": ["trivial", "spt", "afm"],
            "s": [float(ss[v % len(ss)]) for v in rows.values()],
            "delta": [float(ds[v // len(ss)]) for v in rows.values()],
        }
    )
    print("rows:", pts.set_index("curve")[["s", "delta"]].to_dict(orient="index"))
    qs = np.linspace(0.0, 2 * np.pi, args.nq)
    df = pd.DataFrame({"q": qs})
    for name, k in rows.items():
        df[name] = structure_factor(psi[k].astype(np.complex128), qs)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    df.to_csv(args.out, index=False)
    pts_path = os.path.join(os.path.dirname(args.out), "Sq_points.csv")
    pts.to_csv(pts_path, index=False)
    print(f"wrote {args.out} ({len(df)} q-points) + {pts_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""热力图：只读 CSV 渲染，不做任何物理重算（ZR/string/AFM 三量共用）。

用法：
    python shared/viz/plot_heatmap.py [--csv PATH] [--png PATH] [--no-pdf]
        [--value-col COL] [--title T] [--cbar-label L] [--cmap NAME]
        [--vmin V --vmax V [--vcenter C]]

输入缺失/表头不符时以非零退出码失败并打印可读错误，且不产生残缺图片
（先写临时文件再原子 rename）。
"""

import argparse
import os
import sys
import tempfile
from typing import NoReturn

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm


def fail(msg: str) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_grid(csv_path: str, value_col: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    required = ("s", "delta", value_col)
    if not os.path.isfile(csv_path):
        fail(f"input CSV not found: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:  # noqa: BLE001
        fail(f"cannot parse CSV {csv_path}: {e}")
    missing = [c for c in required if c not in df.columns]
    if missing:
        fail(f"CSV {csv_path} missing columns: {missing} (need {list(required)})")
    ss = np.sort(df["s"].unique())
    ds = np.sort(df["delta"].unique())
    if len(df) != len(ss) * len(ds):
        fail(f"CSV {csv_path} is not a full Cartesian grid: {len(df)} rows != {len(ss)}x{len(ds)}")
    grid = df.pivot(index="delta", columns="s", values=value_col).to_numpy()
    return ss, ds, grid


def render(
    ss: np.ndarray,
    ds: np.ndarray,
    grid: np.ndarray,
    title: str,
    cmap: str = "RdBu",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    vcenter: float | None = 0.0,
    cbar_label: str | None = None,
    cbar_ticks: list[float] | None = None,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 5.2), dpi=150)
    if vcenter is None:
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
    else:
        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    im = ax.imshow(
        grid,
        extent=(ss[0], ss[-1], ds[0], ds[-1]),
        origin="lower",
        aspect="auto",
        cmap=cmap,
        norm=norm,
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(cbar_label if cbar_label is not None else "")
    if cbar_ticks is not None:
        cbar.set_ticks(cbar_ticks)
    ax.set_xlabel("s")
    ax.set_ylabel(r"$\delta$")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def atomic_save(fig: plt.Figure, path: str) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_heatmap_", suffix=os.path.splitext(path)[1], dir=d)
    os.close(fd)
    try:
        fig.savefig(tmp, dpi=150)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot heatmap from CSV triplets.")
    ap.add_argument("--csv", default="task1_baseline/data/interim/tilde_ZR_L8_OBC.csv")
    ap.add_argument("--png", default="task1_baseline/data/figures/tilde_ZR_heatmap.png")
    ap.add_argument("--no-pdf", action="store_true", help="skip same-name PDF output")
    ap.add_argument("--value-col", default="tilde_ZR")
    ap.add_argument("--title", default=r"$\tilde{Z}_\mathcal{R}$ (L=8, $n=2$)")
    ap.add_argument("--cbar-label", default=r"$\tilde{Z}_\mathcal{R}$")
    ap.add_argument("--cmap", default="RdBu")
    ap.add_argument("--vmin", type=float, default=-1.0)
    ap.add_argument("--vmax", type=float, default=1.0)
    ap.add_argument("--vcenter", type=float, default=0.0)
    ap.add_argument(
        "--no-vcenter",
        action="store_true",
        help="use sequential Normalize instead of diverging TwoSlopeNorm",
    )
    ap.add_argument("--cbar-ticks", type=float, nargs="*", default=[-1, 0, 1])
    args = ap.parse_args()

    ss, ds, grid = load_grid(args.csv, args.value_col)
    fig = render(
        ss,
        ds,
        grid,
        args.title,
        cmap=args.cmap,
        vmin=args.vmin,
        vmax=args.vmax,
        vcenter=None if args.no_vcenter else args.vcenter,
        cbar_label=args.cbar_label,
        cbar_ticks=args.cbar_ticks,
    )
    atomic_save(fig, args.png)
    print(f"wrote {args.png}")
    if not args.no_pdf:
        pdf = os.path.splitext(args.png)[0] + ".pdf"
        atomic_save(fig, pdf)
        print(f"wrote {pdf}")


if __name__ == "__main__":
    main()

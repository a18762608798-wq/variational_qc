#!/usr/bin/env python
"""能谱画布：一画布两子图（δ=-1/+1），每子图 E0/E1 两条线，只读谱 CSV。

用法：
    python shared/viz/plot_spectra.py [--csv PATH] [--png PATH] [--no-pdf]
        [--title T]

输入缺失/表头不符时以非零退出码失败并打印可读错误，且不产生残缺图片
（先写临时文件再原子 rename，与 plot_heatmap.py 同约定）。
"""

import argparse
import os
import sys
import tempfile
from typing import NoReturn

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def fail(msg: str) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def atomic_save(fig: plt.Figure, path: str) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_spectra_", suffix=os.path.splitext(path)[1], dir=d)
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
    ap = argparse.ArgumentParser(description="Plot E0/E1 spectra canvas from spectra CSV.")
    ap.add_argument("--csv", default="task1_baseline/data/interim/spectra_L8_OBC.csv")
    ap.add_argument("--png", default="task1_baseline/data/figures/spectra.png")
    ap.add_argument("--no-pdf", action="store_true", help="skip same-name PDF output")
    ap.add_argument("--title", default="Spectra (L=8)")
    args = ap.parse_args()

    if not os.path.isfile(args.csv):
        fail(f"input CSV not found: {args.csv}")
    try:
        df = pd.read_csv(args.csv)
    except Exception as e:  # noqa: BLE001
        fail(f"cannot parse CSV {args.csv}: {e}")
    missing = [c for c in ("s", "delta", "E0", "E1") if c not in df.columns]
    if missing:
        fail(f"CSV {args.csv} missing columns: {missing}")

    deltas = sorted(df["delta"].unique())
    if len(deltas) != 2:
        fail(f"expected exactly 2 delta cuts, got {deltas}")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150, sharey=True)
    for ax, d in zip(axes, deltas):
        sub = df[df["delta"] == d].sort_values("s")
        ax.plot(sub["s"], sub["E0"], label=r"$E_0$", color="C0")
        ax.plot(sub["s"], sub["E1"], label=r"$E_1$", color="C1", linestyle="--")
        ax.set_xlabel("s")
        ax.set_title(rf"$\delta={d:g}$")
        ax.legend(loc="best")
    axes[0].set_ylabel("energy")
    fig.suptitle(args.title)
    fig.tight_layout()

    atomic_save(fig, args.png)
    print(f"wrote {args.png}")
    if not args.no_pdf:
        pdf = os.path.splitext(args.png)[0] + ".pdf"
        atomic_save(fig, pdf)
        print(f"wrote {pdf}")


if __name__ == "__main__":
    main()

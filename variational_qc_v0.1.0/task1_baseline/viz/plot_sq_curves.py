#!/usr/bin/env python
"""S(q) 三线示意图：只读 Sq_curves.csv，三相各一条归一化曲线，同轴绘制。

纵轴归一 S/8（与 S̃ 热力图同语言，Néel 峰顶 1）。输入缺失时非零退出，
先写临时文件再原子 rename，不残留半文件。

用法：python task1_baseline/viz/plot_sq_curves.py [--csv PATH] [--png PATH] [--no-pdf]
"""

import argparse
import os
import sys
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REQUIRED_COLS = ("q", "S_trivial", "S_spt", "S_afm")

CURVE_COLS = (("trivial", "S_trivial"), ("spt", "S_spt"), ("afm", "S_afm"))


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def atomic_save(fig: plt.Figure, path: str) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_sq_", suffix=os.path.splitext(path)[1], dir=d)
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
    ap = argparse.ArgumentParser(description="Plot normalized S(q) curves for three phases.")
    ap.add_argument("--csv", default="task1_baseline/data/interim/Sq_curves.csv")
    ap.add_argument("--png", default="task1_baseline/data/figures/Sq_curves.png")
    ap.add_argument("--no-pdf", action="store_true", help="skip same-name PDF output")
    args = ap.parse_args()

    if not os.path.isfile(args.csv):
        fail(f"input CSV not found: {args.csv}")
    try:
        df = pd.read_csv(args.csv)
    except Exception as e:  # noqa: BLE001
        fail(f"cannot parse CSV {args.csv}: {e}")
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        fail(f"CSV {args.csv} missing columns: {missing}")
    pts_path = os.path.join(os.path.dirname(args.csv), "Sq_points.csv")
    if not os.path.isfile(pts_path):
        fail(f"points file not found: {pts_path}")
    try:
        pts = pd.read_csv(pts_path).set_index("curve")
    except Exception as e:  # noqa: BLE001
        fail(f"cannot parse {pts_path}: {e}")

    def label(name: str) -> str:
        try:
            s, d = float(pts.loc[name, "s"]), float(pts.loc[name, "delta"])
        except KeyError:
            fail(f"{pts_path} missing curve: {name}")
        return f"{name} ({round(s, 2):g}, {round(d, 2):g})"

    fig, ax = plt.subplots(figsize=(7, 4.6), dpi=150)
    for name, col in CURVE_COLS:
        ax.plot(df["q"].to_numpy(), (df[col] / 8.0).to_numpy(), label=label(name))
    ax.axvline(np.pi, linestyle="--", linewidth=1)
    ax.set_xlabel("q")
    ax.set_ylabel(r"$\tilde{S}(q)$")
    ax.set_title(r"$\tilde{S}(q)$ (L=8)")
    ax.set_xlim(0.0, 2 * np.pi)
    ax.set_xticks([0.0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
    ax.set_xticklabels(["0", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"])
    ax.legend()
    fig.tight_layout()
    atomic_save(fig, args.png)
    print(f"wrote {args.png}")
    if not args.no_pdf:
        pdf = os.path.splitext(args.png)[0] + ".pdf"
        atomic_save(fig, pdf)
        print(f"wrote {pdf}")


if __name__ == "__main__":
    main()

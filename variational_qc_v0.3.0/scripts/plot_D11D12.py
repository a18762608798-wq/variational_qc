"""exp06 T005 出图（零机时）：D11 散点+误差棒 + D12 归一化比较。

4 面板 (2δ × {S(π), string})，p=1,2,3 三色；D11 真机散点+std 棒，
D12 真机组 + D10 引用线（各自归一化）。
风格：figure_style.py，mathtext，矢量 PDF + 300dpi PNG → figs/exp06/。
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figure_style import apply_figure_style  # noqa: E402
from exp06_common import DATA_DIR, FIGS_DIR  # noqa: E402

PALETTE = apply_figure_style()
FIGS_DIR.mkdir(parents=True, exist_ok=True)
COLORS = ["C0", "C1", "C2"]
PANELS = [("spi", r"$S(\pi)$"), ("ostr", r"$O_{\rm str}$")]


def main() -> None:
    d11 = np.load(DATA_DIR / "exp06_D11.npz")
    d12 = np.load(DATA_DIR / "exp06_D12.npz")
    s_idx = d11["s_idx"]
    s_vals = np.array(sorted(set(s_idx.tolist()))) / 100.0

    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.0), sharex=True)
    for ri, di in enumerate((1, 2)):
        delta = float(d11["deltas"][d11["delta_idx"] == di][0])
        for ci, (key, label) in enumerate(PANELS):
            ax = axes[ri][ci]
            for p, c in zip((1, 2, 3), COLORS):
                m = (d11["delta_idx"] == di) & (d11["p"] == p)
                o = np.argsort(d11["s_idx"][m])
                ax.errorbar(d11["s_idx"][m][o] / 100.0, d11[f"{key}_mean"][m][o],
                            yerr=d11[f"{key}_std"][m][o], fmt="o", color=c,
                            markersize=3, capsize=2, label=f"p={p}")
            ax.set_title(f"δ={delta}, {label}")
            ax.set_xlabel("s")
            ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS_DIR / "exp06_D11.pdf")
    fig.savefig(FIGS_DIR / "exp06_D11.png", dpi=300)
    plt.close(fig)
    print("wrote figs/exp06/exp06_D11.pdf + .png")

    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.0), sharex=True)
    for ri, di in enumerate((1, 2)):
        delta = float(d11["deltas"][d11["delta_idx"] == di][0])
        for ci, (key, label) in enumerate(PANELS):
            ax = axes[ri][ci]
            nkey = f"d{di}_{key}"
            m = d12["delta_idx"] == di
            o = np.argsort(d12["s_idx"][m])
            ax.plot(d12["s_idx"][m][o] / 100.0, d12[f"{nkey}_ref"][o], "-",
                    color="gray", label="simulator")
            for p, c in zip((1, 2, 3), COLORS):
                mp = m & (d12["p"] == p)
                op = np.argsort(d12["s_idx"][mp])
                ax.plot(d12["s_idx"][mp][op] / 100.0,
                        d12[f"{nkey}_hw"][mp][op], "o", color=c,
                        markersize=3, label=f"hw p={p}")
            ax.set_title(f"δ={delta}, {label} (normalized)")
            ax.set_xlabel("s")
            ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS_DIR / "exp06_D12.pdf")
    fig.savefig(FIGS_DIR / "exp06_D12.png", dpi=300)
    plt.close(fig)
    print("wrote figs/exp06/exp06_D12.pdf + .png")


if __name__ == "__main__":
    main()

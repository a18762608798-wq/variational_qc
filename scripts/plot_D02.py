"""D02 appendix plots (exp03 T006): three separate figures (a)=D02a / (b)=D02b / (c)=D02c.

Reads data/exp03/exp03_D02.npz only; no physics recomputed.
(a) Delta vs s + per-curve minima (same simple marker),
(b) A vs s + pairwise crossings (20-24 colored with legend; others marker-only),
(c) Delta vs 1/L + LS fit.
Style via the vendored scripts/figure_style.py. Self-checks grids, shapes,
and marker/table agreement before plotting.

Project Python: .CondaPkg/.pixi/envs/default/bin/python.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data", "exp03")
FIGDIR = os.path.join(HERE, "..", "figs", "exp03")

LS = [8, 12, 16, 20, 24]
FIT_LS = [8, 12, 16, 20, 24]
LINESTYLES = ["-", "--", ":", "-.", (0, (3, 1, 1, 1))]
CROSS_MARKERS = ["o", "s", "^", "D", "v", "p", "*", "X", "d", "h"]
PAIR_LABELS = ["8-12", "8-16", "8-20", "8-24", "12-16", "12-20", "12-24", "16-20", "16-24", "20-24"]
HIGHLIGHT = "#CC79A7"  # colored marker for the 12-16 crossing (plan §2)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE

    palette = apply_figure_style()
    d = np.load(os.path.join(DATA, "exp03_D02.npz"))

    assert list(d["Ls"]) == LS
    s_wide = d["s_wide"]
    s_narrow = d["s_narrow"]
    D_wide = d["D_wide"]
    A_narr = d["A_narrow"]
    assert s_wide.shape == (99,) and s_narrow.shape == (99,)
    assert D_wide.shape == (5, 99) and A_narr.shape == (5, 99)
    assert abs(s_wide[49] - 0.5) < 1e-12, "wide grid must contain s=0.5 at i=50"
    assert np.isfinite(D_wide).all() and np.isfinite(A_narr).all()
    cross_s = d["cross_s"]
    cross_A = d["cross_A"]
    assert list(d["cross_pairs"]) == [102, 103, 104, 105, 203, 204, 205, 304, 305, 405]
    assert cross_s.shape == (10,) and cross_A.shape == (10,)
    assert s_narrow[0] < cross_s[4] < s_narrow[-1]
    a, b = float(d["fit_a"]), float(d["fit_b"])
    assert list(d["fit_Ls"]) == FIT_LS
    xs = np.array(d["fit_x"])
    ys = np.array(d["fit_y"])
    assert xs.shape == (5,) and ys.shape == (5,)
    for r in range(5):
        assert abs(ys[r] - D_wide[r, 49]) < 1e-12, "(iii) must reuse (i) s=0.5 point"

    os.makedirs(FIGDIR, exist_ok=True)

    # (a) symmetric gap vs s, minima marked with the same simple marker.
    fig, ax = plt.subplots()
    for r, L in enumerate(LS):
        ax.plot(s_wide, D_wide[r], color=palette[r], linestyle=LINESTYLES[r],
                linewidth=1.5, label=rf"$L={L}$")
        m = D_wide[r].argmin()
        ax.plot(s_wide[m], D_wide[r, m], marker="o", color=palette[r],
                markeredgecolor="black", markeredgewidth=0.8,
                markersize=5, linestyle="None", zorder=3)
    ax.set_xlabel(r"$s$")
    ax.set_ylabel(r"$\Delta_{\mathrm{sec}}$")
    ax.legend(frameon=False, fontsize=7)
    finalize_figure(fig, os.path.join(FIGDIR, "exp03_D02a.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp03_D02a.png"))
    plt.close(fig)

    # (b) scaled gap vs s + pairwise crossings.
    fig, ax = plt.subplots()
    for r, L in enumerate(LS):
        ax.plot(s_narrow, A_narr[r], color=palette[r], linestyle=LINESTYLES[r],
                linewidth=1.5, label=rf"$L={L}$")
    for p in range(10):
        last = (p == 9)  # 20-24: colored marker + legend; others marker-only
        ax.plot(cross_s[p], cross_A[p], marker=CROSS_MARKERS[p],
                color="black", markerfacecolor=HIGHLIGHT if last else "white",
                markeredgewidth=0.8, markersize=5, linestyle="None", zorder=3,
                label=rf"${PAIR_LABELS[p]}$: ${cross_s[p]:.3f}$" if last else None)
    ax.set_xlim(0.5, 0.53)
    ax.set_xlabel(r"$s$")
    ax.set_ylabel(r"$A=\Delta_{\mathrm{sec}} L$")
    ax.legend(frameon=False, fontsize=7)
    finalize_figure(fig, os.path.join(FIGDIR, "exp03_D02b.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp03_D02b.png"))
    plt.close(fig)

    # (c) gap vs 1/L (five points) + fit line through L=20,24 only.
    fig, ax = plt.subplots()
    xline = np.array([0.0, xs.max() * 1.1])
    ax.plot(xline, a * xline + b, color="black", linewidth=1.0, linestyle="--")
    for r, L in enumerate(FIT_LS):
        ax.plot(xs[r], ys[r], marker="o", color=palette[r],
                markeredgecolor="black", markersize=5, linestyle="None", zorder=3,
                label=rf"$L={L}$")
    ax.legend(frameon=False, fontsize=7)
    ax.text(0.05, 0.95, rf"$a={a:.2f}$" "\n" rf"$b={b:.2f}$",
            transform=ax.transAxes, ha="left", va="top", fontsize=7)
    ax.set_xlabel(r"$1/L$")
    ax.set_ylabel(r"$\Delta_{\mathrm{sec}}$")
    finalize_figure(fig, os.path.join(FIGDIR, "exp03_D02c.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp03_D02c.png"))
    plt.close(fig)
    print("wrote: figs/exp03/exp03_D02{a,b,c}.pdf + .png")


if __name__ == "__main__":
    main()

"""D01 bare heatmap + D05 three-pair annotated figure (exp01 T005).

Reads data/exp01/exp01_D01.npz only; no physics recomputed here.
Style via the vendored scripts/figure_style.py (scientific-figure-style skill).
Self-checks grids and the three spec pairs before plotting.

Project Python: .CondaPkg/.pixi/envs/default/bin/python.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data", "exp01")
FIGDIR = os.path.join(HERE, "..", "figs", "exp01")

# Three start→end pairs from specs/exp01/spec.md §3 (fixed).
PAIRS = [
    {"phase": "trivial", "start": (0.01, 0.02), "end": (0.21, 0.42)},
    {"phase": "topological", "start": (0.99, 0.02), "end": (0.90, 0.20)},
    {"phase": "afm", "start": (0.50, 1.98), "end": (0.61, 1.44)},
]
END_MARKERS = ["*", "*", "*"]  # ends uniformly stars (spec: distinct from circle starts)


def expected_grids():
    return (np.array([i / 100 for i in range(1, 100)]),
            np.array([j / 50 for j in range(1, 100)]))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE

    palette = apply_figure_style()
    assert len(palette) >= 3, "need ≥3 pair colors"

    z = np.load(os.path.join(DATA, "exp01_D01.npz"))
    s, d = expected_grids()
    assert np.array_equal(z["s_grid"], s), "s_grid mismatch with spec"
    assert np.array_equal(z["delta_grid"], d), "delta_grid mismatch with spec"
    zt = z["z_tilde"]
    assert zt.shape == (99, 99) and np.isfinite(zt).all(), "D01 incomplete"

    # Self-checks: every marker on-grid; exactly three pairs.
    assert len(PAIRS) == 3 and len(END_MARKERS) == 3
    for p in PAIRS:
        for pt in (p["start"], p["end"]):
            assert pt[0] in s and pt[1] in d, f"marker {pt} off-grid"

    os.makedirs(FIGDIR, exist_ok=True)

    def base_heatmap():
        fig, ax = plt.subplots()
        mesh = ax.pcolormesh(s, d, zt.T, shading="auto")
        fig.colorbar(mesh, ax=ax, label=r"$\tilde{Z}_R$")
        ax.set_xlabel(r"$s$")
        ax.set_ylabel(r"$\delta$")
        ax.set_xlim(0.0, 1.0)  # full spec range so edge markers/labels are not clipped
        ax.set_ylim(0.0, 2.0)
        return fig, ax

    # D01 bare (no markers).
    fig, ax = base_heatmap()
    ax.set_title(r"$\tilde{Z}_R$")
    finalize_figure(fig, os.path.join(FIGDIR, "exp01_D01.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp01_D01.png"))
    plt.close(fig)
    print("wrote: figs/exp01/exp01_D01.pdf + .png")

    # D05: three pairs + arrows.
    fig, ax = base_heatmap()
    ax.set_title("State preparation schematic")
    for k, p in enumerate(PAIRS):
        color = palette[k]
        s0, d0 = p["start"]
        s1, d1 = p["end"]
        ax.plot(s0, d0, marker="o", color=color, markeredgecolor="black",
                markersize=7, linestyle="None", zorder=3)
        ax.plot(s1, d1, marker=END_MARKERS[k], color=color,
                markeredgecolor="black", markersize=9, linestyle="None", zorder=3)
        ax.text(s0, d0, f" {p['phase']}-start", color="black", fontsize=7,
                ha="right" if s0 > 0.9 else "left")
        ax.text(s1, d1, f" {p['phase']}-end", color="black", fontsize=7,
                ha="right" if s1 > 0.9 else "left")
        ax.annotate("", xy=(s1, d1), xytext=(s0, d0),
                    arrowprops={"arrowstyle": "->", "color": color,
                                "linewidth": 1.2, "shrinkA": 6, "shrinkB": 7})
    finalize_figure(fig, os.path.join(FIGDIR, "exp01_D05.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp01_D05.png"))
    plt.close(fig)
    print("wrote: figs/exp01/exp01_D05.pdf + .png")

    meta = {"pairs": PAIRS,
            "figure": "figs/exp01/exp01_D05.png",
            "figure_bare": "figs/exp01/exp01_D01.png",
            "style": {"helper": "scripts/figure_style.py (skill scientific-figure-style vendored copy)",
                      "pair_colors": palette[:3], "end_markers": END_MARKERS,
                      "mathtext": True, "export": "PDF vector master + PNG 300dpi"},
            "python": {"executable": sys.executable, "version": sys.version.split()[0],
                       "numpy": np.__version__,
                       "matplotlib": matplotlib.__version__}}
    with open(os.path.join(FIGDIR, "exp01_D05_markers.json"), "w") as f:
        json.dump(meta, f, indent=1)


if __name__ == "__main__":
    main()

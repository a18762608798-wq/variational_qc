"""D03 three-curve plot + D04 four-panel heatmaps (exp02 T006).

Reads data/exp02/exp02_D03.npz and exp02_D04.npz only; no physics recomputed.
Style via the vendored scripts/figure_style.py. Self-checks grids, shapes,
and the D03<->D04 pi-point agreement before plotting.

Project Python: .CondaPkg/.pixi/envs/default/bin/python.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data", "exp02")
FIGDIR = os.path.join(HERE, "..", "figs", "exp02")

REP_LABELS = ["trivial", "topological", "afm"]
LINESTYLES = ["-", "--", ":"]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE

    palette = apply_figure_style()
    d03 = np.load(os.path.join(DATA, "exp02_D03.npz"))
    d04 = np.load(os.path.join(DATA, "exp02_D04.npz"))

    q = d03["q_grid"]
    curves = d03["curves"]
    assert q.shape == (99,) and curves.shape == (3, 99)
    assert abs(q[49] - np.pi) < 1e-12, "q grid must contain pi at k=50"
    with open(os.path.join(DATA, "exp02_D03_meta.json")) as f:
        assert json.load(f)["rep_labels"] == REP_LABELS

    s = d04["s_grid"]
    d = d04["delta_grid"]
    panels = {k: d04[k] for k in ("s_pi", "o_str", "q_val", "z_tilde")}
    for k, v in panels.items():
        assert v.shape == (99, 99) and np.isfinite(v).all(), f"panel {k} incomplete"
    # D03<->D04 pi-point agreement at rep coords (k=50 -> q=pi).
    # 0-based numpy indices from (s,delta) grid positions 1-based (i,j).
    rep_idx = {"trivial": (0, 0), "topological": (98, 0), "afm": (49, 98)}
    for r, label in enumerate(REP_LABELS):
        i, j = rep_idx[label]
        assert abs(curves[r, 49] - panels["s_pi"][i, j]) < 1e-9, f"D03/D04 pi mismatch {label}"

    os.makedirs(FIGDIR, exist_ok=True)

    # D03: three S(q) curves sharing axes.
    fig, ax = plt.subplots()
    for r, label in enumerate(REP_LABELS):
        ax.plot(q, curves[r], color=palette[r], linestyle=LINESTYLES[r],
                linewidth=1.5, label=label)
    ax.axvline(np.pi, color="black", linewidth=0.6, linestyle=":")
    ax.text(np.pi, -0.032, r"$\pi$", transform=ax.get_xaxis_transform(),
            ha="center", va="center", fontsize=7, clip_on=False)
    peak = curves[2].max()
    ax.plot(np.pi, peak, marker="o", color=palette[2], markeredgecolor="black",
            markersize=5, linestyle="None", zorder=3)
    ax.set_xlabel(r"$q$")
    ax.set_ylabel(r"$S(q)$")
    ax.legend(frameon=False, fontsize=7)
    finalize_figure(fig, os.path.join(FIGDIR, "exp02_D03.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp02_D03.png"))
    plt.close(fig)
    print("wrote: figs/exp02/exp02_D03.pdf + .png")

    # D04: four standalone panels (2x2 composition is latex's job).
    # (a)-(d) live in filenames only, never on the figure.
    panels4 = [(r"$S(\pi)$", "s_pi", "exp02_D04a"),
               (r"$O_{\rm str}$", "o_str", "exp02_D04b"),
               (r"$Q$", "q_val", "exp02_D04c"),
               (r"$\tilde{Z}_R$", "z_tilde", "exp02_D04d")]
    for title, key, stem in panels4:
        fig, ax = plt.subplots()
        mesh = ax.pcolormesh(s, d, panels[key].T, shading="auto")
        fig.colorbar(mesh, ax=ax)
        ax.set_title(title)
        ax.set_xlabel(r"$s$")
        ax.set_ylabel(r"$\delta$")
        fig.tight_layout()
        finalize_figure(fig, os.path.join(FIGDIR, stem + ".pdf"))
        finalize_figure(fig, os.path.join(FIGDIR, stem + ".png"))
        plt.close(fig)
        print(f"wrote: figs/exp02/{stem}.pdf + .png")

    meta = {"rep_labels": REP_LABELS, "linestyles": LINESTYLES,
            "figures": ["figs/exp02/exp02_D03.png",
                        "figs/exp02/exp02_D04a.png",
                        "figs/exp02/exp02_D04b.png",
                        "figs/exp02/exp02_D04c.png",
                        "figs/exp02/exp02_D04d.png"],
            "python": {"executable": sys.executable, "version": sys.version.split()[0],
                       "numpy": np.__version__, "matplotlib": matplotlib.__version__}}
    with open(os.path.join(FIGDIR, "exp02_D034_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)


if __name__ == "__main__":
    main()

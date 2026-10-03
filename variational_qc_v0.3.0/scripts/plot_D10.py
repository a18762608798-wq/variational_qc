"""D10 result curves (exp04 T006): 4 figures = 2 δ-lines x {S(pi), string}.

Reads data/exp04/exp04_D10.npz only; no physics recomputed.
Each figure overlays p = 1, 2, 3. Style via scripts/figure_style.py.
Self-checks grids, shapes, and winner/min-leg agreement before plotting.

Project Python: .CondaPkg/.pixi/envs/default/bin/python.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data", "exp04")
FIGDIR = os.path.join(HERE, "..", "figs", "exp04")

TAGS = ["d0", "d085"]
DELTA_LABELS = [r"$\delta=0$", r"$\delta=0.85$"]
PANELS = [("spi", r"$S(\pi)$"), ("ostr", "string")]
LINESTYLES = ["-", "--", ":"]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE

    palette = apply_figure_style()
    d = np.load(os.path.join(DATA, "exp04_D10.npz"))

    assert list(d["deltas"]) == [0.0, 0.85]
    s = None
    curves = {}
    for tag in TAGS:
        s_grid = d["s_grid"] if s is None else s
        if s is None:
            s = s_grid
        else:
            assert np.array_equal(s, s_grid)
        assert s.shape == (99,)
        E_star = d[f"{tag}_E_star"]
        leg_E = d[f"{tag}_leg_E"]
        a_star = d[f"{tag}_a_star"]
        assert E_star.shape == (99, 3) and leg_E.shape == (99, 3, 3)
        # winner = min leg (bit-exact: same archived floats)
        assert np.array_equal(E_star, leg_E.min(axis=1)), f"{tag} winner mismatch"
        assert set(np.unique(a_star)) <= {1, 2, 3}
        curves[tag] = {k: d[f"{tag}_{k}"] for k in ("spi", "ostr")}
        for k, v in curves[tag].items():
            assert v.shape == (99, 3) and np.isfinite(v).all(), f"{tag}/{k} incomplete"

    os.makedirs(FIGDIR, exist_ok=True)
    for tag, dlabel in zip(TAGS, DELTA_LABELS):
        for key, ylabel in PANELS:
            fig, ax = plt.subplots()
            for p in range(3):
                ax.plot(s, curves[tag][key][:, p], color=palette[p],
                        linestyle=LINESTYLES[p], linewidth=1.5,
                        label=rf"$p={p + 1}$")
            ax.set_xlabel(r"$s$")
            ax.set_ylabel(ylabel)
            ax.set_title(rf"{dlabel} VQE")
            ax.legend(frameon=False, fontsize=7)
            finalize_figure(fig, os.path.join(FIGDIR, f"exp04_D10_{tag}_{key}.pdf"))
            finalize_figure(fig, os.path.join(FIGDIR, f"exp04_D10_{tag}_{key}.png"))
            plt.close(fig)
            print(f"wrote: figs/exp04/exp04_D10_{tag}_{key}.pdf + .png")


if __name__ == "__main__":
    main()

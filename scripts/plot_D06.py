"""D06 ansatz schematic (exp04 T006): zero data input, pure drawing.

Faithful to doc/theory/ansatz.md for L = 8 only:
- odd-bond orbits O1 <-> O4, O2 <-> O3 (shared color per pair);
- even-bond orbits E1 <-> E3, E2 self-mirror;
- one layer = F sublayer then S sublayer (F = first-acting; triv/afm: F = even,
  topo: F = odd);
- p-layer stacking U^(1) -> ... -> U^(p) on |psi_init,a>.
No gate types or connections beyond ansatz.md are drawn.

Project Python: .CondaPkg/.pixi/envs/default/bin/python.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FIGDIR = os.path.join(HERE, "..", "figs", "exp04")


def draw_chain(ax, bonds, title, note):
    """8 sites in a row; bonds drawn as colored arcs above."""
    xs = np.arange(8)
    ax.plot(xs, np.zeros(8), color="black", linewidth=0.8, zorder=1)
    ax.scatter(xs, np.zeros(8), s=36, color="white", edgecolors="black",
               linewidths=0.8, zorder=3)
    for i, x in enumerate(xs):
        ax.text(x, -0.16, rf"${i + 1}$", ha="center", va="top", fontsize=7)
    for (a, b, color, label) in bonds:
        xa, xb = a - 1, b - 1
        xm = (xa + xb) / 2
        arc = Arc((xm, 0), width=abs(xb - xa), height=0.42, theta1=0,
                  theta2=180, color=color, linewidth=1.5)
        ax.add_patch(arc)
        ax.text(xm, 0.26, label, ha="center", va="bottom", fontsize=6, color=color)
    ax.set_xlim(-0.7, 7.7)
    ax.set_ylim(-0.35, 0.62)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)
    ax.text(3.5, -0.33, note, ha="center", va="top", fontsize=6)


def main():
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE

    palette = apply_figure_style()
    cO1, cO2 = palette[0], palette[1]
    cE1, cE2 = palette[2], palette[3]

    os.makedirs(FIGDIR, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 3.4))

    # Top: odd-bond orbits (one layer, odd sublayer).
    draw_chain(axes[0],
               [(1, 2, cO1, r"$O_1$"), (7, 8, cO1, r"$O_1$"),
                (3, 4, cO2, r"$O_2$"), (5, 6, cO2, r"$O_2$")],
               r"odd sublayer $U_o$: orbits $O_1\leftrightarrow O_4$, $O_2\leftrightarrow O_3$",
               r"each orbit one $(\theta_1,\theta_2)$; bond $R_{XX}R_{YY}R_{ZZ}$")
    # Bottom: even-bond orbits (one layer, even sublayer).
    draw_chain(axes[1],
               [(2, 3, cE1, r"$E_1$"), (6, 7, cE1, r"$E_3$"),
                (4, 5, cE2, r"$E_2$")],
               r"even sublayer $U_e$: orbits $E_1\leftrightarrow E_3$, $E_2$ self-mirror",
               r"$F$ acts first: triv/afm $F=e$, topo $F=o$; $U^{(l)}=U^{(l)}_SU^{(l)}_F$, $p=1,2,3$")

    fig.tight_layout()
    fig.text(0.5, 0.01,
             r"$|\psi_{\mathrm{triv}}\rangle=$ odd-bond singlets;  "
             r"$|\psi_{\mathrm{topo}}\rangle=|s\rangle_{1,8}+$ even-bond singlets;  "
             r"$|\psi_{\mathrm{AFM}}\rangle=$ GHZ",
             ha="center", va="bottom", fontsize=6)
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06.pdf + .png")


if __name__ == "__main__":
    main()

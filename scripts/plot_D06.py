"""D06a-c per-phase schematics (exp04 T009): zero data input, pure drawing.

Faithful to doc/theory/psi0.md + doc/theory/ansatz.md for L = 8 only:
- D06a trivial: init = odd-bond singlets; F = even acts first (U_o U_e).
- D06b topo: init = |s>_{1,8} + even-bond singlets; F = odd acts first (U_e U_o).
- D06c AFM: init = GHZ (no singlets); F = even acts first (U_o U_e).
Orbit colors/pairing shared across figures:
- odd-bond orbits O1 <-> O4, O2 <-> O3 (shared color per pair);
- even-bond orbits E1 <-> E3, E2 self-mirror.
Each layer U^(l) = U^(l)_S U^(l)_F, layers stack U^(1) -> ... -> U^(p).
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

GRAY = "0.45"


def draw_chain(ax, bonds, title, note, arc_height=0.42, label_y=0.26,
               ymax=0.62):
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
        arc = Arc((xm, 0), width=abs(xb - xa), height=arc_height, theta1=0,
                  theta2=180, color=color, linewidth=1.5)
        ax.add_patch(arc)
        ax.text(xm, label_y, label, ha="center", va="bottom", fontsize=6,
                color=color)
    ax.set_xlim(-0.7, 7.7)
    ax.set_ylim(-0.35, ymax)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)
    ax.text(3.5, -0.33, note, ha="center", va="top", fontsize=6)


def draw_F_e(ax, cE1, cE2):
    """First-acting even sublayer (triv/afm): same bonds as before."""
    draw_chain(ax,
               [(2, 3, cE1, r"$E_1$"), (6, 7, cE1, r"$E_3$"),
                (4, 5, cE2, r"$E_2$")],
               r"first $F=e$: even sublayer $U_e$ ($E_1\leftrightarrow E_3$, $E_2$ self-mirror)",
               r"each orbit one $(\theta_1,\theta_2)$; bond $R_{XX}R_{YY}R_{ZZ}$")


def draw_S_o(ax, cO1, cO2):
    """Second-acting odd sublayer (triv/afm)."""
    draw_chain(ax,
               [(1, 2, cO1, r"$O_1$"), (7, 8, cO1, r"$O_1$"),
                (3, 4, cO2, r"$O_2$"), (5, 6, cO2, r"$O_2$")],
               r"then $S=o$: odd sublayer $U_o$ ($O_1\leftrightarrow O_4$, $O_2\leftrightarrow O_3$)",
               r"$U^{(l)}=U^{(l)}_SU^{(l)}_F$; layers $U^{(1)}\to\cdots\to U^{(p)}$")


def draw_F_o(ax, cO1, cO2):
    """First-acting odd sublayer (topo)."""
    draw_chain(ax,
               [(1, 2, cO1, r"$O_1$"), (7, 8, cO1, r"$O_1$"),
                (3, 4, cO2, r"$O_2$"), (5, 6, cO2, r"$O_2$")],
               r"first $F=o$: odd sublayer $U_o$ ($O_1\leftrightarrow O_4$, $O_2\leftrightarrow O_3$)",
               r"each orbit one $(\theta_1,\theta_2)$; bond $R_{XX}R_{YY}R_{ZZ}$")


def draw_S_e(ax, cE1, cE2):
    """Second-acting even sublayer (topo)."""
    draw_chain(ax,
               [(2, 3, cE1, r"$E_1$"), (6, 7, cE1, r"$E_3$"),
                (4, 5, cE2, r"$E_2$")],
               r"then $S=e$: even sublayer $U_e$ ($E_1\leftrightarrow E_3$, $E_2$ self-mirror)",
               r"$U^{(l)}=U^{(l)}_SU^{(l)}_F$; layers $U^{(1)}\to\cdots\to U^{(p)}$")


def main():
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE

    palette = apply_figure_style()
    cO1, cO2 = palette[0], palette[1]
    cE1, cE2 = palette[2], palette[3]

    os.makedirs(FIGDIR, exist_ok=True)

    # --- D06a trivial: odd-bond singlet product; F = e. ---
    fig, axes = plt.subplots(3, 1, figsize=(7.0, 5.0))
    draw_chain(axes[0],
               [(1, 2, GRAY, r"$|s\rangle$"), (3, 4, GRAY, r"$|s\rangle$"),
                (5, 6, GRAY, r"$|s\rangle$"), (7, 8, GRAY, r"$|s\rangle$")],
               r"init $|\psi_{\rm triv}\rangle=\bigotimes_j|s\rangle_{2j-1,2j}$: odd-bond singlets",
               r"gray = initial singlets (not orbit bonds)")
    draw_F_e(axes[1], cE1, cE2)
    draw_S_o(axes[2], cO1, cO2)
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06a.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06a.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06a.pdf + .png")

    # --- D06b topo: |s>_{1,8} + even-bond singlets; F = o. ---
    fig, axes = plt.subplots(3, 1, figsize=(7.0, 5.4))
    draw_chain(axes[0],
               [(2, 3, GRAY, r"$|s\rangle$"), (4, 5, GRAY, r"$|s\rangle$"),
                (6, 7, GRAY, r"$|s\rangle$")],
               r"init $|\psi_{\rm topo}\rangle=|s\rangle_{1,8}\otimes_j|s\rangle_{2j,2j+1}$",
               r"gray = initial singlets (not orbit bonds)",
               ymax=1.45)
    axes[0].add_patch(Arc((3.5, 0), width=7, height=2.2, theta1=0,
                          theta2=180, color=GRAY, linewidth=1.5))
    axes[0].text(3.5, 1.18, r"$|s\rangle_{1,8}$", ha="center", va="bottom",
                 fontsize=6, color=GRAY)
    draw_F_o(axes[1], cO1, cO2)
    draw_S_e(axes[2], cE1, cE2)
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06b.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06b.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06b.pdf + .png")

    # --- D06c AFM: GHZ (no singlets); F = e. ---
    fig, axes = plt.subplots(3, 1, figsize=(7.0, 5.0))
    ax = axes[0]
    xs = np.arange(8)
    ax.plot(xs, np.zeros(8), color="black", linewidth=0.8, zorder=1)
    ax.scatter(xs, np.zeros(8), s=36, color="white", edgecolors="black",
               linewidths=0.8, zorder=3)
    for i, x in enumerate(xs):
        ax.text(x, -0.16, rf"${i + 1}$", ha="center", va="top", fontsize=7)
    ax.plot([-0.5, 7.5], [0.42, 0.42], color=GRAY, linewidth=1.5)
    ax.plot([-0.5, -0.5], [0.30, 0.42], color=GRAY, linewidth=1.5)
    ax.plot([7.5, 7.5], [0.30, 0.42], color=GRAY, linewidth=1.5)
    ax.text(3.5, 0.46,
            r"init $|\psi_{\rm AFM}\rangle=(|0101\cdots\rangle+|1010\cdots\rangle)/\sqrt{2}$",
            ha="center", va="bottom", fontsize=7, color=GRAY)
    ax.set_xlim(-0.7, 7.7)
    ax.set_ylim(-0.35, 0.72)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(r"init: GHZ, no singlet pairs", fontsize=8)
    ax.text(3.5, -0.33, r"gray bracket = global superposition (not bonds)",
            ha="center", va="top", fontsize=6)
    draw_F_e(axes[1], cE1, cE2)
    draw_S_o(axes[2], cO1, cO2)
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06c.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06c.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06c.pdf + .png")


if __name__ == "__main__":
    main()

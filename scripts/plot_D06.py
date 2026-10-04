"""D06a-c per-phase schematics (exp04 T009): zero data input, pure drawing.

Circuit-leaning hybrid (not a literal qiskit circuit):
- 8 horizontal qubit wires (site 1 top = logical 0), time flows left to right;
- left column: init-state two-qubit links (gray bars; GHZ links follow
  qmeas.models.xxz pidx=0 middle-out CNOT fan-out, X/H omitted);
- then two layer blocks U^(1) and U^(k) joined by vertical dots;
- each block: F then S sublayer gate boxes (one rounded box per bond,
  orbit colors; same color = shared (theta, phi)).
Faithful to doc/theory/psi0.md + doc/theory/ansatz.md for L = 8 only:
- D06a trivial: odd-bond singlet pairs; F = even (U_o U_e).
- D06b topo: |s>_{1,8} link + even-bond singlet pairs; F = odd (U_e U_o).
- D06c AFM: GHZ adjacent-link chain; F = even (U_o U_e).
Orbit colors/groups (same color = shared parameters):
group 1 = odd-outer pair bonds (1,2)&(7,8), group 2 = odd-inner pair
(3,4)&(5,6), group 3 = even-outer pair (2,3)&(6,7), group 4 = even-central
bond (4,5) self-mirror. Box text only carries indexed thetas, no orbit
letters: theta^{(l)}_{g1} / theta^{(l)}_{g2} with g = group, l = layer.
No gate types beyond ansatz.md are drawn.

Project Python: .CondaPkg/.pixi/envs/default/bin/python.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FIGDIR = os.path.join(HERE, "..", "figs", "exp04")

GRAY = "0.45"
N = 8


def y_of(site):
    """Site 1..8 top-down (site 1 = logical 0, qiskit-style top)."""
    return N - site


GAP_L, GAP_R = 4.75, 6.25  # 与两侧 layer_frame 内边对齐


def draw_wires(ax, x0=0.0, x1=10.4):
    xs = np.arange(N)
    for i in range(N):
        y = y_of(i + 1)
        ax.plot([x0, GAP_L], [y] * 2, color="black", linewidth=0.8,
                zorder=1)
        ax.plot([GAP_R, x1], [y] * 2, color="black", linewidth=0.8,
                zorder=1)
        # 间隙内每线一根横虚线（省略的中间层），代替竖省略号。
        ax.plot([GAP_L, GAP_R], [y] * 2, color="black", linewidth=0.8,
                linestyle=(0, (2, 2)), zorder=1)
        ax.scatter([x0], [y], s=36, color="white",
                   edgecolors="black", linewidths=0.8, zorder=3)
        ax.text(x0 - 0.25, y, rf"${i + 1}$", ha="right",
                va="center", fontsize=7)
    ax.arrow(x1 + 0.1, -1.3, 0.6, 0, head_width=0.18, head_length=0.18,
             fc="black", ec="black")
    ax.text(x1 + 0.45, -1.65, "time steps", ha="center", va="top",
            fontsize=7)


def link_bar(ax, a, b, x):
    """Gray vertical bar linking two wires = one two-qubit init link."""
    ya, yb = y_of(a), y_of(b)
    ax.plot([x, x], [yb, ya], color=GRAY, linewidth=3.0, solid_capstyle="round")


def gate_box(ax, a, b, x, color, group, layer):
    """One orbit bond gate box spanning two wires."""
    ya, yb = y_of(a), y_of(b)
    box = FancyBboxPatch((x - 0.5, yb - 0.32), 1.0, ya - yb + 0.64,
                         boxstyle="round,pad=0.02", facecolor="white",
                         edgecolor=color, linewidth=1.6)
    ax.add_patch(box)
    ax.text(x, (ya + yb) / 2, f"$\\theta^{{({layer})}}_{{{group}}}$" + "\n"
            f"$\\varphi^{{({layer})}}_{{{group}}}$", ha="center",
            va="center", fontsize=8, color=color, linespacing=1.8)


def layer_frame(ax, x0, x1):
    frame = FancyBboxPatch((x0, -0.45), x1 - x0, 8.0,
                           boxstyle="round,pad=0.05", facecolor="none",
                           edgecolor="black", linewidth=1.0,
                           linestyle=(0, (4, 3)))
    ax.add_patch(frame)


def draw_sublayer(ax, bonds, x, layer):
    for (a, b), g in bonds:
        gate_box(ax, a, b, x, GROUP_COLORS[g], g, layer)


def finish(ax):
    ax.set_xlim(-0.9, 11.6)
    ax.set_ylim(-1.9, 9.0)
    ax.set_aspect("equal")
    ax.axis("off")


# Orbit groups: same group + color = one shared (theta, phi).
ODD_BONDS = [((1, 2), 1), ((7, 8), 1),
             ((3, 4), 2), ((5, 6), 2)]
EVEN_BONDS = [((2, 3), 3), ((6, 7), 3),
              ((4, 5), 4)]
GROUP_COLORS: dict = {}

# Column x positions: init | U^(1): F, S | dots | U^(k): F, S.
X_INIT, X_F1, X_S1, X_FK, X_SK = 0.55, 2.2, 4.0, 7.0, 8.8


def main():
    from figure_style import apply_figure_style, finalize_figure

    palette = apply_figure_style()
    global GROUP_COLORS
    GROUP_COLORS = {1: palette[0], 2: palette[1],
                    3: palette[2], 4: palette[3]}

    os.makedirs(FIGDIR, exist_ok=True)

    # --- D06a trivial: odd-bond singlet pairs; F = even. ---
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    draw_wires(ax)
    for a, b in [(1, 2), (3, 4), (5, 6), (7, 8)]:
        link_bar(ax, a, b, X_INIT)
    ax.text(X_INIT, 8.0, r"$|\psi_{\rm triv}\rangle$", ha="center",
            va="bottom", fontsize=8)
    draw_sublayer(ax, EVEN_BONDS, X_F1, "1")
    draw_sublayer(ax, ODD_BONDS, X_S1, "1")
    layer_frame(ax, X_F1 - 0.75, X_S1 + 0.75)
    ax.text((X_F1 + X_S1) / 2, 8.0, r"$U^{(1)}$", ha="center",
            va="bottom", fontsize=7)
    draw_sublayer(ax, EVEN_BONDS, X_FK, "k")
    draw_sublayer(ax, ODD_BONDS, X_SK, "k")
    layer_frame(ax, X_FK - 0.75, X_SK + 0.75)
    ax.text((X_FK + X_SK) / 2, 8.0, r"$U^{(k)}$", ha="center",
            va="bottom", fontsize=7)
    finish(ax)
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06a.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06a.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06a.pdf + .png")

    # --- D06b topo: (1,8) link + even-bond pairs; F = odd. ---
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    draw_wires(ax)
    for a, b in [(2, 3), (4, 5), (6, 7)]:
        link_bar(ax, a, b, X_INIT)
    link_bar(ax, 1, 8, X_INIT + 0.35)
    ax.text(X_INIT, 8.0, r"$|\psi_{\rm topo}\rangle$", ha="center",
            va="bottom", fontsize=8)
    draw_sublayer(ax, ODD_BONDS, X_F1, "1")
    draw_sublayer(ax, EVEN_BONDS, X_S1, "1")
    layer_frame(ax, X_F1 - 0.75, X_S1 + 0.75)
    ax.text((X_F1 + X_S1) / 2, 8.0, r"$U^{(1)}$", ha="center",
            va="bottom", fontsize=7)
    draw_sublayer(ax, ODD_BONDS, X_FK, "k")
    draw_sublayer(ax, EVEN_BONDS, X_SK, "k")
    layer_frame(ax, X_FK - 0.75, X_SK + 0.75)
    ax.text((X_FK + X_SK) / 2, 8.0, r"$U^{(k)}$", ha="center",
            va="bottom", fontsize=7)
    finish(ax)
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06b.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06b.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06b.pdf + .png")

    # --- D06c AFM: adjacent-link GHZ chain (qmeas xxz pidx=0 links);
    # F = even. ---
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    draw_wires(ax)
    # GHZ cascade moments (qmeas xxz pidx=0 middle-out fan-out):
    # middle pair first, outward pairs in later moments, staggered in x.
    for step, pairs in enumerate([[(4, 5), (5, 6)],
                                  [(3, 4), (6, 7)],
                                  [(2, 3), (7, 8)],
                                  [(1, 2)]]):
        x0 = 0.30 + 0.32 * step
        xs = [x0 - 0.09, x0 + 0.09] if len(pairs) == 2 else [x0]
        for (a, b), x in zip(pairs, xs):
            link_bar(ax, a, b, x)
    ax.text(X_INIT, 8.0, r"$|\psi_{\rm AFM}\rangle$", ha="center",
            va="bottom", fontsize=8)
    draw_sublayer(ax, EVEN_BONDS, X_F1, "1")
    draw_sublayer(ax, ODD_BONDS, X_S1, "1")
    layer_frame(ax, X_F1 - 0.75, X_S1 + 0.75)
    ax.text((X_F1 + X_S1) / 2, 8.0, r"$U^{(1)}$", ha="center",
            va="bottom", fontsize=7)
    draw_sublayer(ax, EVEN_BONDS, X_FK, "k")
    draw_sublayer(ax, ODD_BONDS, X_SK, "k")
    layer_frame(ax, X_FK - 0.75, X_SK + 0.75)
    ax.text((X_FK + X_SK) / 2, 8.0, r"$U^{(k)}$", ha="center",
            va="bottom", fontsize=7)
    finish(ax)
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06c.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06c.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06c.pdf + .png")


if __name__ == "__main__":
    main()

"""D06a-c per-phase schematics (exp04 T009): zero data input, pure drawing.

Circuit-leaning hybrid (not a literal qiskit circuit):
- 8 horizontal qubit wires (site 1 top = logical 0), time flows left to right;
- left column: init-state preparation marks (gray singlet bars / GHZ bracket);
- middle columns: F then S sublayer gate boxes (one rounded box per bond,
  orbit colors, labeled with orbit + (theta1, theta2));
- dashed box = one layer U^(l) = U_S U_F, layers stack U^(1) -> ... -> U^(p).
Faithful to doc/theory/psi0.md + doc/theory/ansatz.md for L = 8 only:
- D06a trivial: odd-bond singlets; F = even (U_o U_e).
- D06b topo: |s>_{1,8} + even-bond singlets; F = odd (U_e U_o).
- D06c AFM: GHZ bracket; F = even (U_o U_e).
Orbit colors/pairing: O1 <-> O4, O2 <-> O3 (shared color per pair);
E1 <-> E3, E2 self-mirror. No gate types beyond ansatz.md are drawn.

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


def draw_wires(ax, x0=0.0, x1=6.2):
    xs = np.arange(N)
    for i in range(N):
        ax.plot([x0, x1], [y_of(i + 1)] * 2, color="black", linewidth=0.8,
                zorder=1)
        ax.scatter([x0], [y_of(i + 1)], s=36, color="white",
                   edgecolors="black", linewidths=0.8, zorder=3)
        ax.text(x0 - 0.25, y_of(i + 1), rf"${i + 1}$", ha="right",
                va="center", fontsize=7)
    ax.arrow(x1 + 0.1, -1.3, 0.6, 0, head_width=0.18, head_length=0.18,
             fc="black", ec="black")
    ax.text(x1 + 0.45, -1.65, "time", ha="center", va="top", fontsize=7)


def singlet_bar(ax, a, b, x, label=None):
    """Gray vertical bar linking two wires = one initial singlet."""
    ya, yb = y_of(a), y_of(b)
    ax.plot([x, x], [yb, ya], color=GRAY, linewidth=3.0, solid_capstyle="round")
    if label:
        ax.text(x + 0.12, (ya + yb) / 2, label, ha="left", va="center",
                fontsize=6, color=GRAY)


def gate_box(ax, a, b, x, color, orbit):
    """One orbit bond gate box spanning two wires."""
    ya, yb = y_of(a), y_of(b)
    box = FancyBboxPatch((x - 0.42, yb - 0.32), 0.84, ya - yb + 0.64,
                         boxstyle="round,pad=0.02", facecolor="white",
                         edgecolor=color, linewidth=1.6)
    ax.add_patch(box)
    ax.text(x, (ya + yb) / 2, f"${orbit}$\n"
            r"$(\theta_1,\theta_2)$", ha="center", va="center",
            fontsize=6, color=color, linespacing=0.9)


def layer_frame(ax, x0, x1, label):
    frame = FancyBboxPatch((x0, -1.0), x1 - x0, 9.2,
                           boxstyle="round,pad=0.05", facecolor="none",
                           edgecolor="black", linewidth=1.0,
                           linestyle=(0, (4, 3)))
    ax.add_patch(frame)
    ax.text((x0 + x1) / 2, 8.55, label, ha="center", va="bottom", fontsize=7)


def finish(ax, title):
    ax.set_xlim(-0.9, 7.0)
    ax.set_ylim(-1.9, 9.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)


ODD_BONDS = [((1, 2), "O_1"), ((7, 8), "O_1"),
             ((3, 4), "O_2"), ((5, 6), "O_2")]
EVEN_BONDS = [((2, 3), "E_1"), ((6, 7), "E_3"),
              ((4, 5), "E_2",)]


def draw_sublayer(ax, bonds, x, colors, title):
    for (a, b), orb in bonds:
        gate_box(ax, a, b, x, colors[orb], orb)
    ax.text(x, 8.0, title, ha="center", va="bottom", fontsize=7)


def main():
    from figure_style import apply_figure_style, finalize_figure

    palette = apply_figure_style()
    cO = {"O_1": palette[0], "O_2": palette[1]}
    cE = {"E_1": palette[2], "E_3": palette[2], "E_2": palette[3]}

    os.makedirs(FIGDIR, exist_ok=True)

    # --- D06a trivial: odd singlets; F = e (U_o U_e). ---
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    draw_wires(ax)
    for (a, b), _ in [((1, 2), None), ((3, 4), None),
                      ((5, 6), None), ((7, 8), None)]:
        singlet_bar(ax, a, b, 0.55, r"$|s\rangle$")
    ax.text(0.55, 8.0, r"init $|\psi_{\rm triv}\rangle$", ha="center",
            va="bottom", fontsize=7)
    draw_sublayer(ax, EVEN_BONDS, 2.3, cE, r"$F=e$: $U_e$")
    draw_sublayer(ax, ODD_BONDS, 4.1, cO, r"$S=o$: $U_o$")
    layer_frame(ax, 1.55, 4.85, r"one layer $U^{(l)}=U^{(l)}_SU^{(l)}_F$"
                r", layers $U^{(1)}\to\cdots\to U^{(p)}$")
    finish(ax, r"D06a trivial: odd-singlet init, even acts first")
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06a.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06a.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06a.pdf + .png")

    # --- D06b topo: |s>_{1,8} + even singlets; F = o (U_e U_o). ---
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    draw_wires(ax)
    for (a, b) in [(2, 3), (4, 5), (6, 7)]:
        singlet_bar(ax, a, b, 0.55, r"$|s\rangle$")
    singlet_bar(ax, 1, 8, 0.05, None)
    ax.text(0.05, 7.35, r"$|s\rangle_{1,8}$", ha="center", va="bottom",
            fontsize=6, color=GRAY)
    ax.text(0.55, 8.0, r"init $|\psi_{\rm topo}\rangle$", ha="center",
            va="bottom", fontsize=7)
    draw_sublayer(ax, ODD_BONDS, 2.3, cO, r"$F=o$: $U_o$")
    draw_sublayer(ax, EVEN_BONDS, 4.1, cE, r"$S=e$: $U_e$")
    layer_frame(ax, 1.55, 4.85, r"one layer $U^{(l)}=U^{(l)}_SU^{(l)}_F$"
                r", layers $U^{(1)}\to\cdots\to U^{(p)}$")
    finish(ax, r"D06b topo: $|s\rangle_{1,8}$ + even singlets, odd acts first")
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06b.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06b.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06b.pdf + .png")

    # --- D06c AFM: GHZ bracket; F = e (U_o U_e). ---
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    draw_wires(ax)
    ax.plot([0.35, 0.35], [y_of(8) - 0.2, y_of(1) + 0.2], color=GRAY,
            linewidth=2.0, solid_capstyle="round")
    ax.plot([0.35, 0.6], [y_of(8) - 0.2] * 2, color=GRAY, linewidth=2.0)
    ax.plot([0.35, 0.6], [y_of(1) + 0.2] * 2, color=GRAY, linewidth=2.0)
    ax.text(0.7, 7.45, r"init $|\psi_{\rm AFM}\rangle$", ha="center",
            va="bottom", fontsize=7, color=GRAY)
    ax.text(2.75, -1.55,
            r"$|\psi_{\rm AFM}\rangle=\frac{|0101\cdots\rangle"
            r"+|1010\cdots\rangle}{\sqrt{2}}$",
            ha="center", va="top", fontsize=7, color=GRAY)
    draw_sublayer(ax, EVEN_BONDS, 2.6, cE, r"$F=e$: $U_e$")
    draw_sublayer(ax, ODD_BONDS, 4.4, cO,
                  r"$S=o$: $U_o$")
    layer_frame(ax, 1.85, 5.15, r"one layer $U^{(l)}=U^{(l)}_SU^{(l)}_F$"
                r", layers $U^{(1)}\to\cdots\to U^{(p)}$")
    finish(ax, r"D06c AFM: GHZ init, even acts first")
    fig.tight_layout()
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06c.pdf"))
    finalize_figure(fig, os.path.join(FIGDIR, "exp04_D06c.png"))
    plt.close(fig)
    print("wrote: figs/exp04/exp04_D06c.pdf + .png")


if __name__ == "__main__":
    main()

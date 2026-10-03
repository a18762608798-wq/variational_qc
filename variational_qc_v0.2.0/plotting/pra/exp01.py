"""PRA publication figures for Experiment 01 — saved data only (v2).

Constrained by `pra-paper-figures` + experiment specs; style changes here
MUST NOT require physics reruns (VII). PDF is the submission original;
PNG (600dpi) is the same-source preview.
"""

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib import pyplot as plt

from plotting.diagnostic.exp01_scaling import fit_scaling
from plotting.pra_check import check_figure
from plotting.pra_style import PRA_PALETTE, apply_pra_style, finalize_figure, style_axes
from plotting.v2read import iter_points

apply_pra_style("single")

_P_STYLE = ["-", "--", "-."]
_P_MARKER = ["o", "s", "^", "D", "v"]


def _checks(out, blocks):
    with open(out / "pra_check.md", "w") as fh:
        fh.write("\n\n".join(blocks) + "\n")


def rebuild_all(data_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    blocks = []
    grid = [r for r in iter_points(data_dir, "exp01") if r.get("status") == "ok"]
    gaps = [r for r in iter_points(data_dir, "exp01gap") if r.get("status") == "ok"]

    if grid:
        s = sorted({r["s"] for r in grid})
        d = sorted({r["delta"] for r in grid})
        Z = np.full((len(d), len(s)), np.nan)
        lut = {(r["s"], r["delta"]): r["ZtR"] for r in grid}
        for i, dd in enumerate(d):
            for j, ss in enumerate(s):
                Z[i, j] = lut.get((ss, dd), np.nan)
        fig, ax = plt.subplots()
        im = ax.imshow(Z, origin="lower", aspect="auto",
                       extent=[min(s), max(s), min(d), max(d)])
        style_axes(ax, "$s$", r"$\delta$")
        fig.colorbar(im, ax=ax, label=r"$\tilde Z_R$")
        fig.tight_layout()
        finalize_figure(fig, out / "phase_pra.pdf")
        finalize_figure(fig, out / "phase_pra.png")
        blocks.append(check_figure(
            fig, "phase_pra",
            caption="Ground-state normalized topological marker "
                    r"$\tilde Z_R(s,\delta)$ on the L=8 interior grid; "
                    "yellow ≈ +1 (trivial), dark ≈ −1 (topological).",
            risk="heatmap colormap choice affects lobe perception; "
                 "data range verified [-1, +1]."))
        plt.close(fig)
        made.append(str(out / "phase_pra.pdf"))

    if gaps:
        dline = sorted({r["delta"] for r in gaps})
        fig, ax = plt.subplots()
        # Appendix style (2026-10-01): plain color straight lines, no
        # markers/linestyles. S(q) dual encoding elsewhere is unchanged.
        for k, L in enumerate(sorted({r["L"] for r in gaps})):
            pts = sorted((r["s"], r["draw"]) for r in gaps if r["L"] == L)
            ax.plot([p[0] for p in pts], [p[1] for p in pts],
                    color=PRA_PALETTE[k % len(PRA_PALETTE)],
                    label=f"$L={int(L)}$")
        style_axes(ax, "$s$", r"$\Delta_{\rm raw}$")
        ax.legend(frameon=False)
        fig.tight_layout()
        finalize_figure(fig, out / "gaps_pra.pdf")
        finalize_figure(fig, out / "gaps_pra.png")
        blocks.append(check_figure(
            fig, "gaps_pra",
            caption=f"Raw full-Hilbert-space gaps at δ={dline[0]:g} for "
                    "L=8,12,16; the s→1 collapse is the OBC edge-state "
                    "splitting, kept as raw spectrum.",
            risk="legend order must match panel curves after any restyle."))
        plt.close(fig)
        made.append(str(out / "gaps_pra.pdf"))

        sc = [(1.0 / r["L"], r["draw"]) for r in gaps if r["s"] == 0.5]
        if sc:
            xs = np.array([p[0] for p in sc])
            ys = np.array([p[1] for p in sc])
            a, b = fit_scaling(xs, ys)
            fig, ax = plt.subplots()
            ax.scatter(xs, ys, s=8, color=PRA_PALETTE[0])
            xx = np.array([0.0, max(xs)])
            style_axes(ax, "$1/L$", r"$\Delta_{\rm raw}(s=0.5)$")
            ax.plot(xx, a * xx + b, color="black", linewidth=1.0)
            ax.text(0.05, 0.9, rf"$a={a:.4g},\ b={b:.4g}$",
                    transform=ax.transAxes, va="top")
            fig.tight_layout()
            finalize_figure(fig, out / "scaling_pra.pdf")
            finalize_figure(fig, out / "scaling_pra.png")
            blocks.append(check_figure(
                fig, "scaling_pra",
                caption="Finite-size scaling at s=0.5 with free-intercept "
                        "linear fit (coefficients labeled in-panel).",
                risk="fit is post-processing only; never feeds physics."))
            plt.close(fig)
            made.append(str(out / "scaling_pra.pdf"))
    _checks(out, blocks)
    return made

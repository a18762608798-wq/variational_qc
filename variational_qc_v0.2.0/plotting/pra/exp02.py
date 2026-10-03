"""PRA publication figures for Experiment 02 — saved data only (v2)."""

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib import pyplot as plt

from plotting.pra_check import check_figure
from plotting.pra_style import PRA_PALETTE, apply_pra_style, finalize_figure, style_axes
from plotting.v2read import iter_points

apply_pra_style("single")


def _pivot(recs, key):
    s = sorted({r["s"] for r in recs})
    d = sorted({r["delta"] for r in recs})
    Z = np.full((len(d), len(s)), np.nan)
    lut = {(r["s"], r["delta"]): r[key] for r in recs}
    for i, dd in enumerate(d):
        for j, ss in enumerate(s):
            Z[i, j] = lut.get((ss, dd), np.nan)
    return s, d, Z


_REP_STYLE = {"afm": (PRA_PALETTE[0], "-", "o"),
              "topological": (PRA_PALETTE[1], "--", "s"),
              "trivial": (PRA_PALETTE[2], ":", "^")}


def _checks(out, blocks):
    with open(out / "pra_check.md", "w") as fh:
        fh.write("\n\n".join(blocks) + "\n")


def rebuild_all(data_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    blocks = []
    heat = [r for r in iter_points(data_dir, "exp02") if r.get("status") == "ok"]
    curves = [r for r in iter_points(data_dir, "exp02sq") if r.get("status") == "ok"]

    if curves:
        fig, ax = plt.subplots()
        for r in sorted(curves, key=lambda r: r["rep"]):
            c, ls, mk = _REP_STYLE.get(r["rep"], (PRA_PALETTE[0], "-", "o"))
            ax.plot(np.asarray(r["q"]), np.asarray(r["Sq"]), ls, marker=mk,
                    markevery=4, markersize=3, color=c, label=r["rep"])
        style_axes(ax, "$q$", "$S(q)$")
        ax.legend(frameon=False)
        fig.tight_layout()
        finalize_figure(fig, out / "sq_pra.pdf")
        finalize_figure(fig, out / "sq_pra.png")
        blocks.append(check_figure(
            fig, "sq_pra",
            caption="$S(q)$ for the trivial/topological/AFM representatives; "
                    "the AFM peak at $q=\\pi$ motivates keeping $S(\\pi)$.",
            risk="trivial/topological curves overlap closely by physics; "
                 "kept distinguishable via color+linestyle+marker."))
        plt.close(fig)
        made.append(str(out / "sq_pra.pdf"))

    for key, name, lab in (("Spi", "S_pi", r"$S(\pi)$"),
                           ("Ostr", "Ostr", "$O_{str}$"),
                           ("Q", "Q", "$Q$"),
                           ("ZtR", "ZtR", r"$\tilde Z_R$")):
        if not heat:
            continue
        s, d, Z = _pivot(heat, key)
        fig, ax = plt.subplots()
        im = ax.imshow(Z, origin="lower", aspect="auto",
                       extent=[min(s), max(s), min(d), max(d)])
        style_axes(ax, "$s$", r"$\delta$")
        fig.colorbar(im, ax=ax, label=lab)
        fig.tight_layout()
        finalize_figure(fig, out / f"{name}_pra.pdf")
        finalize_figure(fig, out / f"{name}_pra.png")
        blocks.append(check_figure(
            fig, f"{name}_pra",
            caption=f"L=8 {lab} heatmap over the interior phase grid.",
            risk="none beyond colormap perception."))
        plt.close(fig)
        made.append(str(out / f"{name}_pra.pdf"))
    _checks(out, blocks)
    return made

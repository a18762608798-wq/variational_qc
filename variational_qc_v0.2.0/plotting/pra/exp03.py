"""PRA reference curves for Experiment 03 — saved data only (v2)."""

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from plotting.pra_check import check_figure
from plotting.pra_style import PRA_PALETTE, apply_pra_style, finalize_figure, style_axes
from plotting.v2read import iter_reference

apply_pra_style("single")

_D_STYLE = [(PRA_PALETTE[0], "-", "o"), (PRA_PALETTE[1], "--", "s")]


def _checks(out, blocks):
    with open(out / "pra_check.md", "w") as fh:
        fh.write("\n\n".join(blocks) + "\n")


def rebuild_all(data_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = list(iter_reference(data_dir))
    made = []
    blocks = []
    for key, lab in (("E0", "$E_0$"), ("Spi", r"$S(\pi)$"), ("Ostr", "$O_{str}$")):
        fig, ax = plt.subplots()
        for k, d in enumerate(sorted({r["delta"] for r in recs})):
            pts = sorted((r["s"], r[key]) for r in recs if r["delta"] == d)
            c, ls, mk = _D_STYLE[k % len(_D_STYLE)]
            ax.plot([p[0] for p in pts], [p[1] for p in pts], ls, marker=mk,
                    markevery=7, markersize=3, color=c, label=rf"$\delta={d:g}$")
        style_axes(ax, "$s$", lab)
        ax.legend(frameon=False)
        fig.tight_layout()
        finalize_figure(fig, out / f"ref_{key}_pra.pdf")
        finalize_figure(fig, out / f"ref_{key}_pra.png")
        blocks.append(check_figure(
            fig, f"ref_{key}_pra",
            caption=f"Exact L=8 {lab}(s) reference on δ=0,0.85 scan lines.",
            risk="none."))
        plt.close(fig)
        made.append(str(out / f"ref_{key}_pra.pdf"))
    _checks(out, blocks)
    return made

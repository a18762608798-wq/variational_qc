"""PRA comparison figures for Experiment 04 — saved data only (v2)."""

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from plotting.pra_check import check_figure
from plotting.pra_style import PRA_PALETTE, apply_pra_style, finalize_figure, style_axes
from plotting.v2read import iter_points, iter_reference

apply_pra_style("single")

_P_MARKER = ["o", "s", "^"]

_DTAG = {0.0: "0", 0.85: "085"}

_PS = (1, 2, 3)


def _checks(out, blocks):
    with open(out / "pra_check.md", "w") as fh:
        fh.write("\n\n".join(blocks) + "\n")


def rebuild_all(ref_dir, var_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ref = {(r["s"], r["delta"]): r for r in iter_reference(ref_dir)}
    sel = [r for r in iter_points(var_dir, "exp04s") if r.get("status") == "ok"]
    made = []
    blocks = []
    for key, rkey, lab in (("Evar", "E0", "$E$"), ("Spi", "Spi", r"$S(\pi)$"),
                           ("Ostr", "Ostr", "$O_{str}$")):
        for d in sorted({r["delta"] for r in sel}):
            dtag = _DTAG[float(d)]
            fig, ax = plt.subplots()
            er = sorted((r["s"], ref[(r["s"], r["delta"])][rkey])
                        for r in sel if r["delta"] == d)
            ax.plot([p[0] for p in er], [p[1] for p in er], "k--", label="exact")
            for k, p in enumerate(sorted({r["p"] for r in sel})):
                if int(p) not in _PS:
                    continue
                pts = sorted((r["s"], r[key]) for r in sel
                             if r["delta"] == d and r["p"] == p)
                ax.plot([q[0] for q in pts], [q[1] for q in pts],
                        color=PRA_PALETTE[k % len(PRA_PALETTE)],
                        marker=_P_MARKER[k % len(_P_MARKER)],
                        markevery=max(1, len(pts) // 3),
                        markersize=3, label=f"$p={int(p)}$")
            ax.text(0.05, 0.95, f"$\\delta={d:g}$", transform=ax.transAxes,
                    va="top", ha="left")
            style_axes(ax, "$s$", lab)
            ax.legend(frameon=False)
            fig.tight_layout()
            stem = f"cmp_{key}_d{dtag}_pra"
            finalize_figure(fig, out / f"{stem}.pdf")
            finalize_figure(fig, out / f"{stem}.png")
            blocks.append(check_figure(
                fig, stem,
                caption=f"Exact vs variational {lab}(s) at "
                        f"$\\delta={d:g}$ per depth; depth improvement reads "
                        "as approach to the dashed exact curve.",
                risk="one delta per panel; depths color + 3 markers per series."))
            plt.close(fig)
            made.append(str(out / f"{stem}.pdf"))
    _checks(out, blocks)
    return made

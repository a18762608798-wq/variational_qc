"""Diagnostic comparison figures for Experiment 04 — saved data only."""


import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from plotting.v2read import iter_points, iter_reference

_DTAG = {0.0: "0", 0.85: "085"}

_P_MARKER = ["o", "s", "^"]

_PS = (1, 2, 3)


def _selected(var_dir):
    return [r for r in iter_points(var_dir, "exp04s") if r.get("status") == "ok"]


def rebuild_all(ref_dir, var_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ref = {(r["s"], r["delta"]): r for r in iter_reference(ref_dir)}
    sel = _selected(var_dir)
    made = []
    for key, rkey, title in (("Evar", "E0", "E"), ("Spi", "Spi", "S(pi)"),
                             ("Ostr", "Ostr", "Ostr")):
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
                        marker=_P_MARKER[k % len(_P_MARKER)],
                        markevery=max(1, len(pts) // 3),
                        label=f"p={int(p)}")
            ax.text(0.05, 0.95, f"delta={d:g}", transform=ax.transAxes,
                    va="top", ha="left")
            ax.set_xlabel("s")
            ax.set_ylabel(f"{title} (delta={d:g})")
            ax.legend()
            ax.set_title(f"{title}(s) exact vs variational, "
                         f"delta={d:g} (diagnostic)")
            fig.savefig(out / f"cmp_{key}_d{dtag}_diag.png")
            plt.close(fig)
            made.append(str(out / f"cmp_{key}_d{dtag}_diag.png"))
    return made

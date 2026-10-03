"""Diagnostic figures for Experiment 02 — saved data only."""

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib import pyplot as plt

from plotting.v2read import iter_points


def _pivot(recs, key):
    s = sorted({r["s"] for r in recs})
    d = sorted({r["delta"] for r in recs})
    Z = np.full((len(d), len(s)), np.nan)
    lut = {(r["s"], r["delta"]): r[key] for r in recs}
    for i, dd in enumerate(d):
        for j, ss in enumerate(s):
            Z[i, j] = lut.get((ss, dd), np.nan)
    return s, d, Z


def rebuild_all(data_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    heat = [r for r in iter_points(data_dir, "exp02") if r.get("status") == "ok"]
    curves = [r for r in iter_points(data_dir, "exp02sq") if r.get("status") == "ok"]

    if curves:
        # Distinct markers/linestyles: topo/trivial overlap almost exactly and
        # must stay distinguishable (same data, honest rendering, no offsets).
        styles = {"afm": ("-", "o"), "topological": ("--", "s"),
                  "trivial": (":", "^")}
        fig, ax = plt.subplots()
        for r in sorted(curves, key=lambda r: r["rep"]):
            ls, mk = styles.get(r["rep"], ("-", "o"))
            ax.plot(np.asarray(r["q"]), np.asarray(r["Sq"]), ls, marker=mk,
                    markevery=4, label=r["rep"])
        ax.set_xlabel("q")
        ax.set_ylabel("S(q)")
        ax.legend()
        ax.set_title("S(q) representatives (diagnostic)")
        fig.savefig(out / "sq_diag.png")
        plt.close(fig)
        made.append(str(out / "sq_diag.png"))

    for key, name in (("Spi", "S_pi"), ("Ostr", "Ostr"), ("Q", "Q"), ("ZtR", "ZtR")):
        if not heat:
            continue
        s, d, Z = _pivot(heat, key)
        fig, ax = plt.subplots()
        ax.imshow(Z, origin="lower", aspect="auto", extent=[min(s), max(s), min(d), max(d)])
        ax.set_xlabel("s")
        ax.set_ylabel("delta")
        ax.set_title(f"{name} heatmap (diagnostic)")
        fig.savefig(out / f"{name}_diag.png")
        plt.close(fig)
        made.append(str(out / f"{name}_diag.png"))
    return made

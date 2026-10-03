"""Diagnostic figures for Experiment 01 — saved data only, never runs physics."""

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib import pyplot as plt

from plotting.diagnostic.exp01_scaling import fit_scaling
from plotting.v2read import iter_points


def rebuild_all(data_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    made = []
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
        ax.imshow(Z, origin="lower", aspect="auto",
                  extent=[min(s), max(s), min(d), max(d)])
        ax.set_xlabel("s")
        ax.set_ylabel("delta")
        ax.set_title("ZtR phase diagram (diagnostic)")
        fig.savefig(out / "phase_diag.png")
        plt.close(fig)
        made.append(str(out / "phase_diag.png"))

    if gaps:
        dline = sorted({r["delta"] for r in gaps})
        fig, ax = plt.subplots()
        for L in sorted({r["L"] for r in gaps}):
            pts = sorted((r["s"], r["draw"]) for r in gaps if r["L"] == L)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], label=f"L={int(L)}")
        ax.set_xlabel("s")
        ax.set_ylabel("Delta_raw")
        ax.legend()
        ax.set_title(f"raw gaps at delta={dline} (diagnostic)")
        fig.savefig(out / "gaps_diag.png")
        plt.close(fig)
        made.append(str(out / "gaps_diag.png"))

        sc = [(1.0 / r["L"], r["draw"]) for r in gaps if r["s"] == 0.5]
        if sc:
            xs = np.array([p[0] for p in sc])
            ys = np.array([p[1] for p in sc])
            a, b = fit_scaling(xs, ys)
            fig, ax = plt.subplots()
            ax.scatter(xs, ys)
            xx = np.array([0.0, max(xs)])
            ax.plot(xx, a * xx + b)
            ax.set_xlabel("1/L")
            ax.set_ylabel("Delta_raw(s=0.5)")
            ax.set_title(f"scaling: a={a:.4g} b={b:.4g} (diagnostic)")
            fig.savefig(out / "scaling_diag.png")
            plt.close(fig)
            made.append(str(out / "scaling_diag.png"))
    return made

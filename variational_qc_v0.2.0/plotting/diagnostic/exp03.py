"""Diagnostic reference curves for Experiment 03 — saved data only."""

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from plotting.v2read import iter_reference


def rebuild_all(data_dir, out_dir):
    import pathlib

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = list(iter_reference(data_dir))
    made = []
    for key, title in (("E0", "E0"), ("Spi", "S(pi)"), ("Ostr", "Ostr")):
        fig, ax = plt.subplots()
        for d in sorted({r["delta"] for r in recs}):
            pts = sorted((r["s"], r[key]) for r in recs if r["delta"] == d)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], label=f"d={d:g}")
        ax.set_xlabel("s")
        ax.set_ylabel(title)
        ax.legend()
        ax.set_title(f"exact {title} (diagnostic)")
        fig.savefig(out / f"ref_{key}_diag.png")
        plt.close(fig)
        made.append(str(out / f"ref_{key}_diag.png"))
    return made

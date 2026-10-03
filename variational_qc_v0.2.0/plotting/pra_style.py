"""PRA matplotlib style helper (vendored from pra-paper-figures skill, single-column default).

Apply PRA-safe defaults (single/1.5/double column), then export
production files with embedded fonts.

Usage:
    from pra_style import apply_pra_style, finalize_figure, PRA_PALETTE
    apply_pra_style(column="single")
    fig, ax = plt.subplots()
    ...
    finalize_figure(fig, "fig1.pdf")
"""

import matplotlib as mpl
import matplotlib.pyplot as plt

# 8.6cm single, ~12.5cm 1.5-col, ~17.6cm double (inches).
PRA_WIDTHS_IN = {"single": 3.39, "1.5": 5.0, "double": 6.93}

# Okabe-Ito, colorblind-safe, in plot order.
PRA_PALETTE = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # bluish green
    "#D55E00",  # vermillion
    "#56B4E9",  # sky blue
    "#CC79A7",  # reddish purple
    "#000000",  # black
]

PRA_LINESTYLES = ["-", "--", "-.", ":"]
PRA_MARKERS = ["o", "s", "^", "D", "v", "x", "+"]


def apply_pra_style(column="single", aspect=0.75):
    """Set PRA-safe rcParams. Call before creating figures."""
    if column not in PRA_WIDTHS_IN:
        raise ValueError(f"column must be one of {list(PRA_WIDTHS_IN)}")
    width = PRA_WIDTHS_IN[column]
    mpl.rcParams.update(
        {
            "figure.figsize": (width, width * aspect),
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
            "savefig.transparent": False,
            # Embeddable fonts; Type 3 rejected by APS production.
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "serif",
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "lines.linewidth": 1.2,  # >= 0.5pt floor with margin
            "lines.markersize": 4,
            "grid.linewidth": 0.5,
            "axes.grid": False,
            "axes.prop_cycle": mpl.cycler(color=PRA_PALETTE),
            "axes.unicode_minus": False,
        }
    )
    return width


def style_axes(ax, xlabel=None, ylabel=None):
    """Apply PRA axis conventions: units in parens, integer-friendly ticks."""
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.tick_params(direction="in", top=True, right=True)
    return ax


def finalize_figure(fig, path, dpi=600):
    """Save with production settings. PDF for submission, PNG as preview."""
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white",
                transparent=False)
    return path


if __name__ == "__main__":  # smoke test: single-column demo
    import numpy as np

    apply_pra_style("single")
    x = np.linspace(0, 10, 200)
    fig, ax = plt.subplots()
    ax.plot(x, np.sin(x), label="A", linestyle="-", marker="None")
    ax.plot(x, np.cos(x), label="B", linestyle="--", marker="None")
    style_axes(ax, "t (ms)", "signal (arb. units)")
    ax.legend(frameon=False)
    finalize_figure(fig, "/tmp/pra_smoke.pdf")
    finalize_figure(fig, "/tmp/pra_smoke.png")
    print("wrote /tmp/pra_smoke.pdf and /tmp/pra_smoke.png")

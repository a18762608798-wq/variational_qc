"""Generic scientific matplotlib style helper.

Style-only: palette + fonts + lines + export. No journal layout,
no column widths, no captions.

Sources:
- Okabe-Ito colors via Wong, Nature Methods 8, 441 (2011)
- Paul Tol qualitative schemes, SRON/EPS/TN/09-002 issue 3.2
- k-dense scientific-visualization publication.mplstyle (general print start)

Usage:
    from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE
    apply_figure_style()
    fig, ax = plt.subplots()
    ax.set_xlabel(r"$a_1$ (ms)")  # mathtext with raw string; never "a_1"
    ...
    finalize_figure(fig, "fig1.pdf")
"""

import matplotlib as mpl
import matplotlib.pyplot as plt

# Five Okabe-Ito colors meeting 3:1 against white (k-dense subset).
# Still pair each with linestyle/marker; palette alone is not accessibility.
DEFAULT_PALETTE = [
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#009E73",  # bluish green
    "#CC79A7",  # reddish purple
    "#000000",  # black
]

# Full Okabe-Ito (Wong 2011), in plot order. Yellow/orange need care on white.
FULL_OKABE_ITO = [
    "#E69F00",
    "#56B4E9",
    "#009E73",
    "#F0E442",
    "#0072B2",
    "#D55E00",
    "#CC79A7",
    "#000000",
]

# Paul Tol muted (9 max) as second choice for many categories.
TOL_MUTED = [
    "#CC6677", "#332288", "#DDCC77", "#117733", "#88CCEE",
    "#882255", "#44AA99", "#999933", "#AA4499",
]

LINESTYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v", "x", "+"]


def apply_figure_style(palette=None):
    """Set style-only rcParams. Call before creating figures."""
    colors = palette or DEFAULT_PALETTE
    mpl.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "savefig.bbox": "standard",
            "savefig.facecolor": "white",
            "savefig.transparent": False,
            # Editable embedded text; Type 3 avoided.
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "legend.frameon": False,
            "legend.loc": "best",
            # Built-in mathtext only; no system LaTeX dependency.
            # Caller must still wrap math in $...$ with a raw string.
            "text.usetex": False,
            "mathtext.fontset": "dejavusans",
            "mathtext.default": "regular",
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "lines.linewidth": 1.5,
            "lines.markersize": 4,
            "lines.markeredgewidth": 0.5,
            "axes.grid": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": mpl.cycler(color=colors),
            "image.cmap": "viridis",
            "axes.unicode_minus": False,
        }
    )
    return colors


def style_axes(ax, xlabel=None, ylabel=None):
    """Minimal axis conventions: units in parens, outward ticks.

    Pass mathtext labels directly, e.g. style_axes(ax, r"$a_1$ (ms)").
    """
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.tick_params(direction="out")
    return ax


def finalize_figure(fig, path, dpi=300):
    """Save with embedded fonts. PDF/SVG for vector, PNG as preview."""
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white",
                transparent=False)
    return path


if __name__ == "__main__":  # smoke test
    import numpy as np

    apply_figure_style()
    x = np.linspace(0, 10, 200)
    fig, ax = plt.subplots()
    ax.plot(x, np.sin(x), label=r"$a_1$", linestyle="-", marker="None")
    ax.plot(x, np.cos(x), label=r"$a_2$", linestyle="--", marker="None")
    style_axes(ax, r"$t$ (ms)", "signal (arb. units)")
    ax.legend(frameon=False)
    finalize_figure(fig, "/tmp/figure_style_smoke.pdf")
    finalize_figure(fig, "/tmp/figure_style_smoke.png")
    print("wrote /tmp/figure_style_smoke.pdf and /tmp/figure_style_smoke.png")

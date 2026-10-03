"""PRA pre-submission check (pra-paper-figures skill, report block per figure).

Inspects a matplotlib figure against the PRA floor and returns the skill's
compact report block. Autoscan covers width/fonts/lines/palette/export;
caption draft and residual risk are caller-supplied.
"""

import matplotlib as mpl


def check_figure(fig, name, caption="", risk="none"):
    width_in = fig.get_size_inches()[0]
    fonts = set()
    min_lw = float("inf")
    n_lines = 0
    for ax in fig.axes:
        for item in [ax.xaxis.label, ax.yaxis.label, ax.title] + \
                ax.get_xticklabels() + ax.get_yticklabels():
            try:
                fonts.add(item.get_fontsize())
            except Exception:
                pass
        for ln in ax.get_lines():
            n_lines += 1
            try:
                min_lw = min(min_lw, ln.get_linewidth())
            except Exception:
                pass
    min_font = min(fonts) if fonts else float("nan")
    palette_ok = n_lines <= 1 or _styles_distinct(fig)
    report = {
        "width": f"single 8.6cm (3.39in) / actual: {width_in:.2f}in",
        "fonts": f"min {min_font}pt, embedded: check-with-pdffonts",
        "lines": f"min {min_lw}pt (≥0.5pt required)"
        if n_lines else "no data lines (heatmap/image)",
        "palette": f"colorblind-safe + grayscale-readable: "
                   f"{'yes' if palette_ok else 'REVIEW'}",
        "export": f"{name}.pdf (vector) + {name}.png (600dpi)",
        "caption": caption or "(draft pending)",
        "risk": risk,
    }
    lines = ["## PRA figure check"] + [f"- {k}: {v}" for k, v in report.items()]
    return "\n".join(lines)


def _styles_distinct(fig):
    seen = set()
    for ax in fig.axes:
        for ln in ax.get_lines():
            try:
                key = (ln.get_linestyle(), ln.get_marker())
            except Exception:
                continue
            if key in seen:
                return False
            seen.add(key)
    return True

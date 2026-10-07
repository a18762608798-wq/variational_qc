---
name: scientific-figure-style
description: Apply consistent matplotlib figure style (palette, fonts, lines, export) without journal layout. Use when the user mentions 画图风格, 配色, 字体, 线宽, colorblind-safe, Okabe-Ito, Tol palette, viridis, or asks to make, revise, or check a scientific figure's visual style — style-only, no column widths, no captions, no REVTeX.
---

# Scientific Figure Style

Style-only guardrail for matplotlib figures: same palette, fonts, and line discipline on every figure. No paper layout.

Why this exists: hand-tuned rcParams drift across figures. A shared helper plus a fixed palette keeps color meaning stable and print-readable. Palette alone is never a compliance claim; always pair color with linestyle/marker.

## Workflow

### 1. Apply style before plotting

```python
from figure_style import apply_figure_style, finalize_figure, DEFAULT_PALETTE
apply_figure_style()
```

Use `scripts/figure_style.py`. It sets a colorblind-safe cycle, embeddable font types, and sane line weights. Do not hand-tune rcParams from scratch; call the helper, then only adjust what the task needs. Figure size is caller-controlled; this skill does not set widths.

Read `references/figure-style-spec.md` for palette sources and limits.

### 2. Build the figure OO-style

- Use `fig, ax = plt.subplots()`; never rely on bare `plt.plot` state for multi-panel work.
- Color + shape redundancy: never encode meaning by color alone. Combine `DEFAULT_PALETTE` order with distinct linestyles/markers so the grayscale version stays readable.
- Forbidden: `jet`/`rainbow`/`turbo` colormaps, red-vs-green as the only contrast, lettering placed over shaded data, legend covering data.
- Axes labels carry units in parentheses: `t (ms)`, `R (10^3 Ω)`. Write `0.2`, not `.2`. Prefer integer ticks; keep equal decimals on one axis.
- Math labels use built-in mathtext: raw string + `$...$`, e.g. `ax.set_xlabel(r"$a_1$ (ms)")`. Bare `a_1` is forbidden. Full LaTeX (`text.usetex`) is out of scope.
- Sequential data: `viridis`/`plasma`/`cividis`. Diverging with a real center: `coolwarm`/`RdBu_r` with explicit norm.

### 3. Export vector master

```python
finalize_figure(fig, "fig1.pdf")   # vector master
finalize_figure(fig, "fig1.png")   # 300dpi preview
```

- Vector PDF/SVG for line art; PNG 300dpi only as preview.
- `bbox_inches="tight"`, `facecolor="white"`, `transparent=False`.
- Grayscale sanity: desaturate a copy; series still separable by style/marker.

## Report structure

Always close with this compact block:

```markdown
## figure style check
- palette: DEFAULT 5-color Okabe-Ito subset / actual: ...
- fonts: sans Arial/Helvetica/DejaVu, embedded Type 42: yes/no
- lines: curves ...pt, axes ...pt
- redundancy: color + linestyle/marker: yes/no
- export: figN.pdf (vector) + figN.png (300dpi)
- remaining risk: ...
```

## Examples

**Example 1:**
Input: 对比两条失谐曲线，统一一下风格
Output: `apply_figure_style()` + 两色+两线型 + `finalize_figure(fig,"fig1.pdf")` + 上面report block

**Example 2:**
Input: 把这个jet图改成色盲友好的
Output: 换DEFAULT_PALETTE+viridis，线宽提至1.0–1.5pt，附grayscale可读说明

# Figure Style Spec (style-only, no journal layout)

Source of truth for palette, fonts, lines, axes, export.
No column widths, no captions, no REVTeX. Size is caller-controlled.

## 1. Palette: data semantics first

- **Qualitative (unordered categories):** default 5-color Okabe-Ito subset
  `#0072B2` `#D55E00` `#009E73` `#CC79A7` `#000000`.
  Source: Wong, Nature Methods 8, 441 (2011). These five meet 3:1 on white.
- **Full Okabe-Ito (8):** add `#E69F00` `#56B4E9` `#F0E442` when needed.
  Yellow `#F0E442` is weak on white; use for fills, not thin lines.
- **Many categories (up to 9):** Paul Tol muted
  `#CC6677 #332288 #DDCC77 #117733 #88CCEE #882255 #44AA99 #999933 #AA4499`.
  Source: SRON/EPS/TN/09-002 issue 3.2. Do not interpolate qualitative palettes.
- **Sequential:** `viridis` / `plasma` / `cividis`. **Diverging with a real center:**
  `coolwarm` / `RdBu_r` with explicit norm. Never `jet` / `rainbow` / `turbo`.
- Palette alone is not accessibility. Every series gets color **plus**
  linestyle or marker. Red-vs-green as sole contrast is forbidden.

## 2. Fonts and text

- One sans family per figure set: `Arial, Helvetica, DejaVu Sans`.
- Sizes: labels/titles 8pt, ticks/legend 7pt (`font.size=8`).
- `pdf.fonttype=42`, `ps.fonttype=42`, `svg.fonttype=none`
  (editable text; appearance depends on installed fonts).
- Numbers: `0.2` not `.2`, decimal point on baseline, same decimals per axis.
- `axes.unicode_minus=False` so minus signs render correctly.
- Mathtext (built-in, no system LaTeX): wrap math in `$...$` with a raw
  string, e.g. `r"$a_1$"`, `r"$\alpha > \beta$"`. Bare `a_1` renders
  literally and is forbidden. Units stay outside math:
  `r"$a_1$ (ms)"`. `text.usetex` stays `False`; full LaTeX is out of scope.
  Math font is `dejavusans` to match the sans stack.

## 3. Lines, markers, axes

- Curves 1.0–1.5pt, axes/ticks ~0.6pt. Grid off by default.
- Markers: `markersize=4`, `markeredgewidth=0.5`.
- Ticks: outward, `major.size=3.0`, `major.width=0.6`.
- Spines: top/right off, left/bottom on.
- OO API: `fig, ax = plt.subplots()`. One Axes = one panel.
- Axis labels carry units in parentheses: `t (ms)`, `R (10^3 Ω)`.
- Legend: `fontsize=7`, `frameon=False`, `loc="best"`.
  Never covers data. Lettering off shaded/image areas where practical.
- Default image cmap is `viridis`.

## 4. Export

- Vector master `.pdf` or `.svg` for line art; `.png` 300dpi for preview.
- `figure.dpi=100`, `savefig.dpi=300`.
- `bbox_inches="tight"`, white background, not transparent.
- Grayscale sanity: desaturate a copy; series still separable by style/marker.

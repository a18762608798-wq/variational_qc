"""exp06 T005 出图（零机时）：D08 四面板叠放比较。

每面板 (2δ × {S(π), string})：模拟机 p=1,2,3 三线（读 D08 存档的 S06
归一化引用值）+ 真机 p* 散点及误差棒（归一化值 + 归一化 std），各自
min-max 归一化后同图（区间见 manifest，可复算）。
p* 取自 manifest（assemble 已按 spec §4 选取并记录）。
风格：figure_style.py，mathtext，矢量 PDF + 300dpi PNG → figs/exp06/。
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figure_style import apply_figure_style  # noqa: E402
from exp06_common import DATA_DIR, FIGS_DIR, read_json  # noqa: E402

PALETTE = apply_figure_style()
FIGS_DIR.mkdir(parents=True, exist_ok=True)
PANELS = [(1, "spi", r"$S(\pi)$", "D08a"), (1, "ostr", r"$O_{\rm str}$", "D08b"),
          (2, "spi", r"$S(\pi)$", "D08c"), (2, "ostr", r"$O_{\rm str}$", "D08d")]
SIM_COLORS = ["#7f7f7f", "#4d4d4d", "#1a1a1a"]


def main() -> None:
    d = np.load(DATA_DIR / "exp06_D08.npz")
    manifest = read_json(DATA_DIR / "exp06_manifest.json")
    p_star = manifest["p_star"]
    intervals = manifest["norm_intervals"]

    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.0), sharex=True)
    for (di, key, label, d08) in PANELS:
        ri, ci = (0 if di == 1 else 1), (0 if key == "spi" else 1)
        ax = axes[ri][ci]
        delta = float(d["deltas"][d["delta_idx"] == di][0])
        m = d["delta_idx"] == di
        nkey = f"d{di}_{key}"
        width = intervals[nkey]["hw"][1] - intervals[nkey]["hw"][0]
        for p, c in zip((1, 2, 3), SIM_COLORS):
            mp = m & (d["p"] == p)
            o = np.argsort(d["s_idx"][mp])
            ax.plot(d["s_idx"][mp][o] / 100.0, d[f"{nkey}_ref"][mp][o],
                    "-", color=c, linewidth=1.0, label=f"sim p={p}")
        ps = int(p_star[d08])
        mh = m & (d["p"] == ps)
        oh = np.argsort(d["s_idx"][mh])
        ax.errorbar(d["s_idx"][mh][oh] / 100.0, d[f"{nkey}_hw"][mh][oh],
                    yerr=d[f"{key}_std"][mh][oh] / width,
                    fmt="o", color="C0", markersize=3, capsize=2,
                    label=f"hw p*={ps}")
        ax.set_title(f"{d08}: δ={delta}, {label} (normalized)")
        ax.set_xlabel("s")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS_DIR / "exp06_D08.pdf")
    fig.savefig(FIGS_DIR / "exp06_D08.png", dpi=300)
    plt.close(fig)
    print("wrote figs/exp06/exp06_D08.pdf + .png")


if __name__ == "__main__":
    main()

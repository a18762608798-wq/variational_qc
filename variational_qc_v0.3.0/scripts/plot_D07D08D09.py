"""exp05 T005 出图（零机时）：8 链 / 10 环前十排名图 + 冠军环子链排名图。

版式规则（用户 2026-10-04 确认）：
- 图上不写具体比特编号，不写内部 D 编号；
- 芯片（Baihua/Shenglian）用 bar 纹理区分 + 图例，不写在刻度上；
- score 堆叠显示：0.8·S̄ 段 + 0.2·F_ro 段（总长 = score）；
- y 轴只标名次 Rank 1..10。
风格：scripts/figure_style.py，mathtext，矢量 PDF + 300dpi PNG → figs/exp05/。
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figure_style import apply_figure_style  # noqa: E402
from exp05_common import DATA_DIR  # noqa: E402

PALETTE = apply_figure_style()
FIGS = Path(__file__).resolve().parent.parent / "figs" / "exp05"
FIGS.mkdir(parents=True, exist_ok=True)

# 芯片 → bar 纹理（刻度上不写芯片名，见图例）。
CHIP_HATCH = {"Baihua": "", "Shenglian": "///"}


def stacked_rank_fig(scores, stabs, fros, chips, title, out) -> None:
    n = len(scores)
    y = np.arange(n)
    comp_s = 0.8 * stabs
    comp_f = 0.2 * fros
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for i in range(n):
        h = CHIP_HATCH.get(str(chips[i]), "")
        ax.barh(i, comp_s[i], color="C1", edgecolor="black",
                hatch=h, linewidth=0.5)
        ax.barh(i, comp_f[i], left=comp_s[i], color="C2",
                edgecolor="black", hatch=h, linewidth=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([f"Rank {i + 1}" for i in range(n)])
    ax.invert_yaxis()
    ax.set_xlabel("score")
    ax.set_title(title)
    legend = [Patch(facecolor="C1", edgecolor="black", label=r"$0.8\,\bar{S}$"),
              Patch(facecolor="C2", edgecolor="black",
                    label=r"$0.2\,F_{\rm ro}$")]
    # 芯片图例固定列出两家（即使某家未进前十，避免读者误以为漏画）。
    for chip in ("Baihua", "Shenglian"):
        legend.append(Patch(facecolor="0.85", edgecolor="black",
                            hatch=CHIP_HATCH.get(chip, ""), label=chip))
    ax.legend(handles=legend, fontsize=8, loc="center left",
              bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    fig.savefig(FIGS / f"{out}.pdf")
    fig.savefig(FIGS / f"{out}.png", dpi=300)
    plt.close(fig)


def main() -> None:
    d07 = np.load(DATA_DIR / "exp05_D07.npz", allow_pickle=True)
    i7 = np.argsort(-d07["score"])[:10]
    stacked_rank_fig(d07["score"][i7], d07["stab_mean"][i7],
                     d07["readout_fid"][i7], d07["chip"][i7],
                     r"$8$-chain ranking top 10", "exp05_D07")

    d08 = np.load(DATA_DIR / "exp05_D08.npz", allow_pickle=True)
    i8 = np.argsort(-d08["score"])[:10]
    stacked_rank_fig(d08["score"][i8], d08["stab_mean"][i8],
                     d08["readout_fid"][i8], d08["chip"][i8],
                     r"$10$-ring ranking top 10", "exp05_D08")

    d09 = np.load(DATA_DIR / "exp05_D09.npz", allow_pickle=True)
    i9 = np.argsort(-d09["score"])
    stacked_rank_fig(d09["score"][i9], d09["stab_mean"][i9],
                     d09["readout_fid"][i9], d09["chip"][i9],
                     r"$8$-subchains in champion ring", "exp05_D09")
    print("出图完成 figs/exp05/")


if __name__ == "__main__":
    main()

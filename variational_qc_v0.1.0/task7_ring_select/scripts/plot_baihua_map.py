"""Baihua 链接图：T1 底色 + 耦合边保真度 + 标记冠军链/4 环/各环最佳 8-子链。

数据源：task6 拓扑快照（本地缓存，零网络请求）。
输出：task7_ring_select/data/figures/baihua_map.png
"""

import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

HERE = Path(__file__).resolve()
ROOT = HERE.parent.parent.parent
QMEAS = ROOT.parent / "03_tools_practice" / "qmeas"

import sys
sys.path.insert(0, str(QMEAS / "src"))
from qmeas.benchmark.topology import usable_edges, is_dead_qubit

TASK7 = HERE.parent.parent

snap = sorted(glob.glob(str(
    ROOT / "task6_qubit_select" / "data" / "topology_cache" / "Baihua_*.json")))[-1]
info = json.load(open(snap))
print("拓扑:", snap.split("/")[-1])

coords, t1 = {}, {}
for label, q in info["qubits_info"].items():
    i = q.get("index", int(label[1:]))
    coords[i] = tuple(q.get("coordinate", (0, 0)))
    t1[i] = q.get("T1") or 0
edges = usable_edges(info)

# 标记集（Baihua）
champion = [67, 68, 69, 70, 71, 72, 73, 74]
rings = [
    [13, 14, 15, 16, 17, 30, 29, 28, 27, 26],
    [69, 70, 71, 72, 73, 86, 85, 84, 83, 82],
    [125, 126, 127, 128, 129, 142, 141, 140, 139, 138],
    [136, 137, 138, 139, 140, 153, 152, 151, 150, 149],
]
best8 = [  # 各环最佳 8-子链（task7 ANALYSIS 表）
    [126, 127, 128, 129, 142, 141, 140, 139],   # 环#1最佳
    [69, 70, 71, 72, 73, 86, 85, 84],           # 环#3最佳
    [28, 27, 26, 13, 14, 15, 16, 17],           # 环#4最佳
    [138, 139, 140, 153, 152, 151, 150, 149],   # 环#5最佳
]

fig, ax = plt.subplots(figsize=(18, 12))
xs = np.array([coords[i][0] for i in coords])
ys = np.array([coords[i][1] for i in coords])

# 底：全部可用边（保真度 colormap）
eseg, ecol = [], []
for (a, b), f in edges.items():
    eseg.append([coords[a], coords[b]])
    ecol.append(f)
lc = LineCollection(eseg, cmap="Blues", alpha=0.55, linewidths=1.2)
lc.set_array(np.array(ecol))
ax.add_collection(lc)

# 底：全部比特（T1 colormap），死比特打 x
alive = [i for i in coords if t1[i] > 0]
dead = [i for i in coords if t1[i] <= 0]
sc = ax.scatter([coords[i][0] for i in alive], [coords[i][1] for i in alive],
                c=[t1[i] for i in alive], cmap="Oranges", s=90, zorder=3,
                edgecolors="k", linewidths=0.4)
plt.colorbar(sc, ax=ax, label="T1 (us)", shrink=0.7)
ax.scatter([coords[i][0] for i in dead], [coords[i][1] for i in dead],
           c="k", marker="x", s=80, zorder=4)
for i in alive:
    ax.text(coords[i][0], coords[i][1], str(i), fontsize=5.5, ha="center",
            va="center", zorder=5)


def draw_path(nodes, close=False, color="red", lw=3.0, ls="-", label=None):
    pts = nodes + ([nodes[0]] if close else [])
    seg = [[coords[a], coords[b]] for a, b in zip(pts, pts[1:])]
    ax.add_collection(LineCollection(seg, colors=color, linewidths=lw,
                                     linestyles=ls, zorder=6))
    if label:
        mx = sum(coords[n][0] for n in nodes) / len(nodes)
        my = sum(coords[n][1] for n in nodes) / len(nodes)
        ax.text(mx, my, label, fontsize=8, color=color, weight="bold",
                ha="center", va="center",
                bbox=dict(fc="white", ec=color, alpha=0.8, pad=1), zorder=7)


for r in rings:
    draw_path(r, close=True, color="blue", lw=2.0)
for b in best8:
    draw_path(b, color="green", lw=3.2)
draw_path(champion, color="red", lw=3.5, label="chain67-74")

from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([0], [0], color="red", lw=3.5, label="champion chain [67..74]"),
    Line2D([0], [0], color="blue", lw=2.0, label="4 Baihua rings (closed)"),
    Line2D([0], [0], color="green", lw=3.2, label="best 8-subchain per ring"),
], loc="best", fontsize=9)

ax.set_aspect("equal")
ax.set_title(f"Baihua connectivity (calib {info.get('calibration_time')}): node color T1, edge color coupler fidelity", fontsize=12)
fig.tight_layout()
out = TASK7 / "data" / "figures"
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / "baihua_map.png", dpi=150)
print("saved:", out / "baihua_map.png")

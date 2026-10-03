"""Baihua 官图 + 标记：拦截 quark 官图绘制，在其坐标系上叠加三类标记后落盘。

背景：quark `save_svg_fname` 在无头 Agg 下静默失败，故拦截 plt.show，
在官方 axes（数据坐标与拓扑快照一致）上画线再 savefig。
输出：task7_ring_select/data/figures/baihua_official_map.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve()
TASK7 = HERE.parent.parent

champion = [67, 68, 69, 70, 71, 72, 73, 74]
rings = [
    [125, 126, 127, 128, 129, 142, 141, 140, 139, 138],
]
best8 = [
    [126, 127, 128, 129, 142, 141, 140, 139],
]

import json, glob
ROOT = HERE.parent.parent.parent
snap = sorted(glob.glob(str(
    ROOT / "task6_qubit_select" / "data" / "topology_cache" / "Baihua_*.json")))[-1]
info = json.load(open(snap))
coords = {}
for label, q in info["qubits_info"].items():
    coords[q.get("index", int(label[1:]))] = tuple(q.get("coordinate", (0, 0)))


def draw_path(ax, nodes, close=False, color="red", lw=4.0):
    pts = nodes + ([nodes[0]] if close else [])
    seg = [[coords[a], coords[b]] for a, b in zip(pts, pts[1:])]
    ax.add_collection(LineCollection(seg, colors=color, linewidths=lw,
                                     zorder=10))


def fake_show(*a, **k):
    fig = plt.gcf()
    ax = fig.axes[0]  # 主拓扑 axes
    for r in rings:
        draw_path(ax, r, close=True, color="blue", lw=3.0)
    for b in best8:
        draw_path(ax, b, color="lime", lw=4.5)
    draw_path(ax, champion, color="red", lw=5.0)
    ax.legend(handles=[
        Line2D([0], [0], color="red", lw=5,
               label="champion chain [67..74]"),
        Line2D([0], [0], color="blue", lw=3,
               label="best ring (closed)"),
        Line2D([0], [0], color="lime", lw=4.5,
               label="best 8-subchain in best ring"),
    ], loc="upper right", fontsize=13)
    out = TASK7 / "data" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "baihua_official_map.png", dpi=150)
    print("saved:", out / "baihua_official_map.png")


plt.show = fake_show

from quark import Task
from qmeas.random.quark_client import quark_token
from qmeas.random import QuarkOptions
tmgr = Task(quark_token(QuarkOptions(chip="Baihua")))
tmgr.backend("Baihua", show_couplers_fidelity=True,
             show_quibts_attributes="T1", highlight_nodes=[],
             save_svg_fname="unused")
print("done")

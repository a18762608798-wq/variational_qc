#!/usr/bin/env python
"""task9 后选择合成：task8 checkpoints -> A/B 过滤 -> CSV。

方案 A：Z 基只留 M=0（8 比特中 1 的个数为 4）字符串，重算 O/S/Q。
方案 B：Z 留 M=0 算 ZZ、X/Y 留偶数个 1 算 XX/YY，拼 H_post（诊断量）。
空集记 NaN，不中断。只读 task8 checkpoints，不写回。

输出 data/interim/：
- vqe_{sym,nosym}_L8_OBC.csv（H_post 分初态列，102 行）
- vqe_{sym,nosym}_Q_L8_OBC.csv（H_post winner 之 Q，102 行）
- vqe_{sym,nosym}_OS_L8_OBC.csv（winner O/S 四列，102 行）
- retention.csv（s,delta,task,init,frac_z_M0,frac_x_even,frac_y_even）
"""

import csv
import glob
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
TASK9 = HERE.parent.parent
ROOT = TASK9.parent
sys.path.insert(0, str(ROOT / "task8_hardware_vqe" / "scripts"))

from analysis import H_from_counts, Q_from_counts  # noqa: E402

INITS = ("triv", "topo", "afm")
NAN = float("nan")


def _bits(hist):
    """直方图 -> [(bitstring 反转后逻辑序 0/1 列表, count)]。"""
    out = []
    for bits, c in hist.items():
        v = [(0 if ch == "0" else 1) for ch in bits[::-1][:8]]
        out.append((v, int(c)))
    return out


def filt_M0(hist):
    """Z 基：只留 M=0（1 的个数为 4）。返回 (过滤直方图, 保留率)。"""
    tot = sum(hist.values())
    kept = {b: c for b, c in hist.items()
            if sum(1 for ch in b[::-1][:8] if ch == "1") == 4}
    return kept, (sum(kept.values()) / tot if tot else 0.0)


def filt_even(hist):
    """X/Y 基：只留偶数个 1。返回 (过滤直方图, 保留率)。"""
    tot = sum(hist.values())
    kept = {b: c for b, c in hist.items()
            if sum(1 for ch in b[::-1][:8] if ch == "1") % 2 == 0}
    return kept, (sum(kept.values()) / tot if tot else 0.0)


def main() -> None:
    pts = {}
    for p in glob.glob(str(ROOT / "task8_hardware_vqe" / "data"
                            / "checkpoints" / "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        m = d["meta"]
        c = d["counts"]
        s, delta = float(m["s"]), float(m["delta"])
        hz, fz = filt_M0(c["Z"])
        hx, fx = filt_even(c["X"])
        hy, fy = filt_even(c["Y"])
        if hz:
            q, o_norm, s_norm = Q_from_counts(hz)
        else:
            q, o_norm, s_norm = NAN, NAN, NAN
        if hz and hx and hy:
            e = H_from_counts(hx, hy, hz, s, delta)
        else:
            e = NAN
        pts[(m["task"], m["init"], delta, s)] = (e, q, o_norm, s_norm,
                                                fz, fx, fy)
    assert len(pts) == 612, len(pts)

    import numpy as np
    ss = list(np.linspace(0.0, 1.0, 51))
    out = TASK9 / "data" / "interim"
    out.mkdir(parents=True, exist_ok=True)
    fmt = lambda v: "nan" if (isinstance(v, float) and math.isnan(v)) \
        else f"{v:.10f}"
    with open(out / "retention.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "task", "init",
                    "frac_z_M0", "frac_x_even", "frac_y_even"])
        for task in ("sym", "nosym"):
            for delta in (-1.0, 1.0):
                for s in ss:
                    for init in INITS:
                        _, _, _, _, fz, fx, fy = pts[
                            (task, init, delta, float(s))]
                        w.writerow([f"{s:.8f}", f"{delta:.8f}", task, init,
                                    f"{fz:.6f}", f"{fx:.6f}", f"{fy:.6f}"])
    for task, estem, qstem, ostem in (
            ("sym", "vqe_sym_L8_OBC.csv", "vqe_sym_Q_L8_OBC.csv",
             "vqe_sym_OS_L8_OBC.csv"),
            ("nosym", "vqe_nosym_L8_OBC.csv", "vqe_nosym_Q_L8_OBC.csv",
             "vqe_nosym_OS_L8_OBC.csv")):
        with open(out / estem, "w", newline="") as fe, \
                open(out / qstem, "w", newline="") as fq, \
                open(out / ostem, "w", newline="") as fo:
            we, wq, wo = csv.writer(fe), csv.writer(fq), csv.writer(fo)
            we.writerow(["s", "delta", "E_triv", "E_topo", "E_afm"])
            wq.writerow(["s", "delta", "Q_vqe"])
            wo.writerow(["s", "delta", "O_norm", "S_norm",
                         "O_str_raw", "S_pi_raw"])
            for delta in (-1.0, 1.0):
                for s in ss:
                    es = [pts[(task, i, delta, float(s))][0] for i in INITS]
                    # winner 按 H_post argmin；全 NaN 则无 winner（Q/OS 记 NaN）
                    order = sorted(range(3),
                                   key=lambda k: (math.isnan(es[k]), es[k]))
                    win = None if all(math.isnan(v) for v in es) else order[0]
                    we.writerow([f"{s:.8f}", f"{delta:.8f}"] +
                                [fmt(v) for v in es])
                    if win is None:
                        wq.writerow([f"{s:.8f}", f"{delta:.8f}", "nan"])
                        wo.writerow([f"{s:.8f}", f"{delta:.8f}"] + ["nan"] * 4)
                    else:
                        _, q, o_norm, s_norm, _, _, _ = pts[
                            (task, INITS[win], delta, float(s))]
                        wq.writerow([f"{s:.8f}", f"{delta:.8f}", fmt(q)])
                        wo.writerow([f"{s:.8f}", f"{delta:.8f}", fmt(o_norm),
                                     fmt(s_norm), fmt(-o_norm if not
                                                     math.isnan(o_norm)
                                                     else NAN),
                                     fmt(s_norm * 8 if not
                                         math.isnan(s_norm) else NAN)])
    print("postselect done: 612 点 A/B 合成完毕")


if __name__ == "__main__":
    main()

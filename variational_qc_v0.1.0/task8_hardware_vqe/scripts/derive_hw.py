#!/usr/bin/env python
"""task8 合成：checkpoints 三基计数 -> H/Q/P CSV（行序与 task3 一致）。

输出：
- data/interim/vqe_sym_L8_OBC.csv / vqe_nosym_L8_OBC.csv（102 行：s,delta,E_triv,E_topo,E_afm）
- data/interim/vqe_sym_Q_L8_OBC.csv / vqe_nosym_Q_L8_OBC.csv（102 行：s,delta,Q_vqe，获胜初态之 Q）
- data/interim/vqe_P_diag.csv（612 行：s,delta,task,init,P_hw，只记录不断言）
"""

import csv
import glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
TASK8 = HERE.parent.parent
sys.path.insert(0, str(TASK8 / "scripts"))

from analysis import H_from_counts, Q_from_counts, P_terms_from_counts  # noqa: E402

INITS = ("triv", "topo", "afm")


def main() -> None:
    pts = {}
    for p in glob.glob(str(TASK8 / "data" / "checkpoints" / "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        m = d["meta"]
        c = d["counts"]
        assert set(c) == {"X", "Y", "Z"}, p
        s, delta = float(m["s"]), float(m["delta"])
        e = H_from_counts(c["X"], c["Y"], c["Z"], s, delta)
        q, o_norm, s_norm = Q_from_counts(c["Z"])
        zt2, px = P_terms_from_counts(c["Z"], c["X"])
        pts[(m["task"], m["init"], delta, s)] = (e, q, zt2 - px,
                                                o_norm, s_norm)
    assert len(pts) == 612, len(pts)

    import numpy as np
    ss = list(np.linspace(0.0, 1.0, 51))
    out = TASK8 / "data" / "interim"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "vqe_P_diag.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "delta", "task", "init", "P_hw"])
        for task in ("sym", "nosym"):
            for delta in (-1.0, 1.0):
                for s in ss:
                    for init in INITS:
                        w.writerow([f"{s:.8f}", f"{delta:.8f}", task, init,
                                    f"{pts[(task, init, delta, float(s))][2]:.10f}"])
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
                    qs = [pts[(task, i, delta, float(s))][1] for i in INITS]
                    we.writerow([f"{s:.8f}", f"{delta:.8f}"] +
                                [f"{v:.10f}" for v in es])
                    win = min(range(3), key=lambda k: es[k])
                    wq.writerow([f"{s:.8f}", f"{delta:.8f}", f"{qs[win]:.10f}"])
                    # 分量输出 + Q 复算一致性（容差 1e-9）
                    _, _, _, o_norm, s_norm = pts[
                        (task, INITS[win], delta, float(s))]
                    q_re = ((1 - 2 * o_norm)
                            - (4.0 / 3.0) * (s_norm - 0.25))
                    assert abs(q_re - qs[win]) < 1e-9, (task, s, delta)
                    wo.writerow([f"{s:.8f}", f"{delta:.8f}",
                                 f"{o_norm:.10f}", f"{s_norm:.10f}",
                                 f"{-o_norm:.10f}", f"{s_norm * 8:.10f}"])
    print("CSVs done: 612 点合成完毕（含 O/S 分量）")


if __name__ == "__main__":
    main()

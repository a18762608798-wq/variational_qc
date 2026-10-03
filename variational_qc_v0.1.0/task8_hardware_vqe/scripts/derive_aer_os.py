#!/usr/bin/env python
"""task8 Aer O/S 导出：task3/task5 thetas -> statevector 精确 O/S。

winner 口径：裸 E argmin（与 task3/5 Q CSV 一致）。
输出 data/interim/vqe_{sym,nosym}_OS_aer_L8_OBC.csv
（表头 s,delta,O_norm,S_norm，102 行），附带 Q 复算校验。
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
TASK8 = HERE.parent.parent
ROOT = TASK8.parent
sys.path.insert(0, str(TASK8 / "scripts"))
sys.path.insert(0, str(ROOT / "task3_vqe" / "scripts"))

from circuits import build_prep  # noqa: E402
from observables import Q_of_state  # noqa: E402
import ansatz as t3  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402

INITS = ("triv", "topo", "afm")


def main() -> None:
    import numpy as np
    ss = list(np.linspace(0.0, 1.0, 51))
    cfgs = {
        "sym": (ROOT / "task3_vqe" / "data" / "interim" / "vqe_thetas.json",
                ROOT / "task3_vqe" / "data" / "interim" / "vqe_L8_OBC.csv",
                ROOT / "task3_vqe" / "data" / "interim" / "vqe_Q_L8_OBC.csv"),
        "nosym": (ROOT / "task5_vqe_nosym" / "depth1" / "data" / "interim"
                  / "vqe_thetas.json",
                  ROOT / "task5_vqe_nosym" / "depth1" / "data" / "interim"
                  / "vqe_L8_OBC.csv",
                  ROOT / "task5_vqe_nosym" / "depth1" / "data" / "interim"
                  / "vqe_Q_L8_OBC.csv"),
    }
    for task, (thp, ecsv, qcsv) in cfgs.items():
        th = json.load(open(thp, encoding="utf-8"))
        edat = {}
        for r in csv.DictReader(open(ecsv, encoding="utf-8")):
            edat[(round(float(r["s"]), 8), round(float(r["delta"]), 8))] = \
                [float(r["E_triv"]), float(r["E_topo"]), float(r["E_afm"])]
        qdat = {}
        for r in csv.DictReader(open(qcsv, encoding="utf-8")):
            qdat[(round(float(r["s"]), 8), round(float(r["delta"]), 8))] = \
                float(r["Q_vqe"])
        out = TASK8 / "data" / "interim" / f"vqe_{task}_OS_aer_L8_OBC.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["s", "delta", "O_norm", "S_norm"])
            for delta in (-1.0, 1.0):
                for s in ss:
                    key = (round(float(s), 8), round(delta, 8))
                    win = INITS[int(np.argmin(edat[key]))]
                    theta = min(th[f"{round(delta, 8)}|{round(float(s), 8)}|{win}"]
                                ["seeds"], key=lambda r: r["fun"])["x"]
                    if task == "sym":
                        psi = np.asarray(Statevector(
                            t3.build_vqe_circuit(win, theta)).data)
                    else:
                        psi = np.asarray(Statevector(
                            build_prep("nosym", win, theta)).data)
                    q, o_norm, s_norm = Q_of_state(psi)
                    assert abs(q - qdat[key]) < 1e-9, (task, s, delta)
                    w.writerow([f"{s:.8f}", f"{delta:.8f}",
                                f"{o_norm:.10f}", f"{s_norm:.10f}"])
        print(f"wrote {out} (Q 复算全过）")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""task1/task2 不变性对比：逐行比较四个 CSV 的对比列与 energies 偏移。

用法（仓库根目录）：
    python task2_hplusp/scripts/compare_task1_task2.py \
        [--task1 task1_baseline] [--task2 task2_hplusp] [--tol 1e-8]

对比列：tilde_ZR、O_str_norm、S_pi_norm、Q（容差内一致为通过）。
energies：task2 - task1 == -1 为预期，偏离行记入异常清单并判失败。
is_degenerate 翻转行单独列出，不判失败（P 劈裂简并子空间为预期内效应）。

通过 exit 0，失败 exit 1；两种情况都打印结论与清单。
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

FILES = {
    "tilde_ZR": ("tilde_ZR_L8_OBC.csv", "tilde_ZR"),
    "O_str_norm": ("Ostr_L8_OBC.csv", "O_str_norm"),
    "S_pi_norm": ("Spi_L8_OBC.csv", "S_pi_norm"),
    "Q": ("Q_L8_OBC.csv", "Q"),
}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare task1 vs task2 CSVs for H+P invariance.")
    ap.add_argument("--task1", default="task1_baseline")
    ap.add_argument("--task2", default="task2_hplusp")
    ap.add_argument("--tol", type=float, default=1e-8)
    args = ap.parse_args()
    tol = args.tol

    ok = True
    diff_rows: list[str] = []

    ref_grid = None
    for label, (fname, col) in FILES.items():
        p1 = os.path.join(args.task1, "data", "interim", fname)
        p2 = os.path.join(args.task2, "data", "interim", fname)
        for p in (p1, p2):
            if not os.path.isfile(p):
                fail(f"input CSV not found: {p}")
        a = pd.read_csv(p1)
        b = pd.read_csv(p2)
        if col not in a.columns:
            fail(f"{p1} missing column: {col}")
        if col not in b.columns:
            fail(f"{p2} missing column: {col}")
        grid = (a["s"].to_numpy(), a["delta"].to_numpy())
        if ref_grid is None:
            ref_grid = grid
        if len(a) != len(b) or not (np.array_equal(grid[0], b["s"].to_numpy())
                                    and np.array_equal(grid[1], b["delta"].to_numpy())):
            fail(f"{fname}: row count or (s,delta) order differs between tasks")
        d = np.abs(a[col].to_numpy() - b[col].to_numpy())
        bad = np.nonzero(d > tol)[0]
        print(f"{label}: {len(a)} rows, max|diff|={d.max():.3e}, off-tol={len(bad)}")
        for k in bad:
            diff_rows.append(
                f"s={a['s'][k]:.8f} delta={a['delta'][k]:.8f} col={label} "
                f"task1={a[col][k]:.10f} task2={b[col][k]:.10f}"
            )
        if len(bad):
            ok = False

    # energies：预期差 -1
    e1 = np.load(os.path.join(args.task1, "data", "interim", "psi_archive.npz"))
    e2 = np.load(os.path.join(args.task2, "data", "interim", "psi_archive.npz"))
    de = e2["energies"] - e1["energies"]
    e_bad = np.nonzero(np.abs(de + 1.0) > tol)[0]
    print(f"energies: {len(de)} rows, shift min={de.min():.3e} max={de.max():.3e}, "
          f"off-(-1)={len(e_bad)}")
    ns = len(e1["s_grid"])
    for k in e_bad:
        s = float(e1["s_grid"][k % ns])
        dlt = float(e1["delta_grid"][k // ns])
        diff_rows.append(
            f"s={s:.8f} delta={dlt:.8f} col=energies "
            f"task1={e1['energies'][k]:.10f} task2={e2['energies'][k]:.10f}"
        )
    if len(e_bad):
        ok = False

    # is_degenerate 翻转：单独列出，不判失败
    g1 = e1["is_degenerate"].astype(int)
    g2 = e2["is_degenerate"].astype(int)
    flip = np.nonzero(g1 != g2)[0]
    print(f"is_degenerate flips (informational): {len(flip)}/{len(g1)}")
    for k in flip[:50]:
        print(f"  flip s/d idx={k} task1={g1[k]} task2={g2[k]}")
    if len(flip) > 50:
        print(f"  ... and {len(flip) - 50} more")

    if diff_rows:
        print(f"--- diff list ({len(diff_rows)}) ---")
        for r in diff_rows[:50]:
            print("  " + r)
        if len(diff_rows) > 50:
            print(f"  ... and {len(diff_rows) - 50} more")
    print("RESULT:", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

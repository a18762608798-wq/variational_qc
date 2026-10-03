#!/usr/bin/env python
"""ZR-like 组合量 Q：只读两个派生 CSV 的归一列，逐行套公式写新 CSV。

定义（doc/model/operator.md）：Q = (1-2*O_str_norm) - (4/3)*(S_pi_norm-1/4)，
平庸 +1、拓扑 -1、AFM 0。纯文件后处理，不碰求解与存档。

用法：python task1_baseline/numerics/derive_q.py [--ostr PATH] [--spi PATH] [--out PATH]
"""

import argparse
import os
import sys

import pandas as pd


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    ap = argparse.ArgumentParser(description="Combine normalized O_str and S_pi into Q.")
    ap.add_argument("--ostr", default="task1_baseline/data/interim/Ostr_L8_OBC.csv")
    ap.add_argument("--spi", default="task1_baseline/data/interim/Spi_L8_OBC.csv")
    ap.add_argument("--out", default="task1_baseline/data/interim/Q_L8_OBC.csv")
    args = ap.parse_args()

    for p in (args.ostr, args.spi):
        if not os.path.isfile(p):
            fail(f"input CSV not found: {p}")
    a = pd.read_csv(args.ostr)
    b = pd.read_csv(args.spi)
    for col in ("O_str_norm",):
        if col not in a.columns:
            fail(f"{args.ostr} missing column: {col}")
    if "S_pi_norm" not in b.columns:
        fail(f"{args.spi} missing column: S_pi_norm")
    if len(a) != len(b) or not ((a["s"] == b["s"]) & (a["delta"] == b["delta"])).all():
        fail("input CSVs differ in rows or (s,delta) order; refusing to join")
    if not (a["is_degenerate"] == b["is_degenerate"]).all():
        fail("is_degenerate columns disagree; refusing to join")

    out = pd.DataFrame({
        "s": a["s"],
        "delta": a["delta"],
        "Q": (1 - 2 * a["O_str_norm"]) - (4.0 / 3.0) * (b["S_pi_norm"] - 0.25),
        "is_degenerate": a["is_degenerate"],
    })
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"wrote {args.out} ({len(out)} rows)")


if __name__ == "__main__":
    main()

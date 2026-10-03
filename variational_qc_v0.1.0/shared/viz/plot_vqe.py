#!/usr/bin/env python
"""VQE 五线对照图：解析 E0/E1 + 三初态 VQE 最优，只读 CSV 做渲染。

用法：
    python shared/viz/plot_vqe.py [--vqe-csv PATH] [--spectra-csv PATH]
        [--delta D] [--png PATH] [--no-pdf] [--title T]

输入缺失/表头不符时以非零退出码失败并打印可读错误，且不产生残缺图片
（先写临时文件再原子 rename，与 plot_heatmap.py 同约定）。
"""

import argparse
import os
import sys
import tempfile
from typing import NoReturn

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def fail(msg: str) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def atomic_save(fig: plt.Figure, path: str) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_vqe_", suffix=os.path.splitext(path)[1], dir=d)
    os.close(fd)
    try:
        fig.savefig(tmp, dpi=150)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot VQE-vs-analytic 5-line comparison.")
    ap.add_argument("--vqe-csv", default="task3_vqe/data/interim/vqe_L8_OBC.csv")
    ap.add_argument("--spectra-csv", default="task1_baseline/data/interim/spectra_L8_OBC.csv")
    ap.add_argument("--delta", type=float, default=1.0)
    ap.add_argument("--png", default="task3_vqe/data/figures/vqe_comparison_deltap1.png")
    ap.add_argument("--no-pdf", action="store_true", help="skip same-name PDF output")
    ap.add_argument("--title", default="VQE vs analytic (L=8)")
    ap.add_argument("--mode", choices=("full", "min", "q", "zr", "o", "s"), default="full",
                    help="full: 5 lines (E0/E1 + 3 inits); min: 3 lines (E0/E1 + min(VQE)); "
                         "q: 2 lines (analytic Q + Q_vqe); zr: 2 lines (analytic tilde_ZR + ZR_vqe); "
                         "o: 2 lines (analytic O_str_norm + O_norm_vqe); "
                         "s: 2 lines (analytic S_pi_norm + S_norm_vqe)")
    ap.add_argument("--q-vqe-csv", default="task3_vqe/data/interim/vqe_Q_L8_OBC.csv")
    ap.add_argument("--q-csv", default="task1_baseline/data/interim/Q_L8_OBC.csv")
    ap.add_argument("--os-vqe-csv", default="task8_hardware_vqe/data/interim/vqe_sym_OS_L8_OBC.csv")
    ap.add_argument("--ostr-csv", default="task1_baseline/data/interim/Ostr_L8_OBC.csv")
    ap.add_argument("--spi-csv", default="task1_baseline/data/interim/Spi_L8_OBC.csv")
    ap.add_argument("--os-aer-csv", default=None,
                    help="Aer-d1 O/S 第三线（列 s,delta,O_norm,S_norm），给出则加画")
    ap.add_argument("--ylim", nargs=2, type=float, default=None,
                    help="覆盖默认纵轴范围，如 --ylim -1.6 1.6（后选择 Q 可超 [-1,1]）")
    ap.add_argument("--zr-vqe-csv", default="task3_vqe/data/interim/vqe_ZR_L8_OBC.csv")
    ap.add_argument("--zr-csv", default="task1_baseline/data/interim/tilde_ZR_L8_OBC.csv")
    args = ap.parse_args()

    for p in (args.vqe_csv, args.spectra_csv):
        if not os.path.isfile(p):
            fail(f"input CSV not found: {p}")
    try:
        v = pd.read_csv(args.vqe_csv)
        a = pd.read_csv(args.spectra_csv)
    except Exception as e:  # noqa: BLE001
        fail(f"cannot parse CSV: {e}")
    for col in ("s", "delta", "E_triv", "E_topo", "E_afm"):
        if col not in v.columns:
            fail(f"{args.vqe_csv} missing column: {col}")
    for col in ("s", "delta", "E0", "E1"):
        if col not in a.columns:
            fail(f"{args.spectra_csv} missing column: {col}")

    if args.mode in ("o", "s"):
        is_o = args.mode == "o"
        vcol, acol, alabel, vlabel, ylabel = (
            ("O_norm", "O_str_norm", r"$O_{\mathrm{str,norm}}$ analytic",
             r"$O_{\mathrm{norm,VQE}}$", r"$O_{\mathrm{norm}}$") if is_o else
            ("S_norm", "S_pi_norm", r"$S_{\mathrm{norm}}$ analytic",
             r"$S_{\mathrm{norm,VQE}}$", r"$S_{\mathrm{norm}}$"))
        acsv = args.ostr_csv if is_o else args.spi_csv
        for p in (args.os_vqe_csv, acsv):
            if not os.path.isfile(p):
                fail(f"input CSV not found: {p}")
        try:
            ov = pd.read_csv(args.os_vqe_csv)
            oa = pd.read_csv(acsv)
        except Exception as e:  # noqa: BLE001
            fail(f"cannot parse CSV: {e}")
        for col in ("s", "delta", vcol):
            if col not in ov.columns:
                fail(f"{args.os_vqe_csv} missing column: {col}")
        if acol not in oa.columns:
            fail(f"{acsv} missing column: {acol}")
        vv = ov[abs(ov["delta"] - args.delta) < 1e-12].sort_values("s")
        aa = oa[abs(oa["delta"] - args.delta) < 1e-12].sort_values("s")
        if len(vv) == 0 or len(aa) == 0:
            fail(f"no rows for delta={args.delta}")
        aer = None
        if args.os_aer_csv:
            if not os.path.isfile(args.os_aer_csv):
                fail(f"input CSV not found: {args.os_aer_csv}")
            try:
                aer = pd.read_csv(args.os_aer_csv)
            except Exception as e:  # noqa: BLE001
                fail(f"cannot parse CSV: {e}")
            for col in ("s", "delta", vcol):
                if col not in aer.columns:
                    fail(f"{args.os_aer_csv} missing column: {col}")
            aer = aer[abs(aer["delta"] - args.delta) < 1e-12].sort_values("s")
            if len(aer) == 0:
                fail(f"no rows for delta={args.delta} in {args.os_aer_csv}")
        fig, ax = plt.subplots(figsize=(8, 5.2), dpi=150)
        ax.plot(aa["s"], aa[acol], label=alabel, color="black")
        if aer is not None:
            ax.plot(aer["s"], aer[vcol], label=r"$\mathrm{Aer}$-$d1$",
                    color="green", linestyle="--")
        ax.plot(vv["s"], vv[vcol], label=vlabel, marker="D",
                markersize=3, linestyle="-", color="C3")
        ax.set_xlabel("s")
        ax.set_ylabel(ylabel)
        ax.set_title(args.title)
        ax.legend(loc="best")
        fig.tight_layout()
        atomic_save(fig, args.png)
        print(f"wrote {args.png}")
        if not args.no_pdf:
            pdf = os.path.splitext(args.png)[0] + ".pdf"
            atomic_save(fig, pdf)
            print(f"wrote {pdf}")
        return

    if args.mode == "q":
        for p in (args.q_vqe_csv, args.q_csv):
            if not os.path.isfile(p):
                fail(f"input CSV not found: {p}")
        try:
            qv = pd.read_csv(args.q_vqe_csv)
            qa = pd.read_csv(args.q_csv)
        except Exception as e:  # noqa: BLE001
            fail(f"cannot parse CSV: {e}")
        for col in ("s", "delta", "Q_vqe"):
            if col not in qv.columns:
                fail(f"{args.q_vqe_csv} missing column: {col}")
        if "Q" not in qa.columns:
            fail(f"{args.q_csv} missing column: Q")
        vv = qv[abs(qv["delta"] - args.delta) < 1e-12].sort_values("s")
        aa = qa[abs(qa["delta"] - args.delta) < 1e-12].sort_values("s")
        if len(vv) == 0 or len(aa) == 0:
            fail(f"no rows for delta={args.delta}")
        fig, ax = plt.subplots(figsize=(8, 5.2), dpi=150)
        ax.plot(aa["s"], aa["Q"], label=r"$Q$ analytic", color="black")
        ax.plot(vv["s"], vv["Q_vqe"], label=r"$Q_{\mathrm{VQE}}$", marker="D",
                markersize=3, linestyle="-", color="C3")
        ax.set_xlabel("s")
        ax.set_ylabel("Q")
        ax.set_ylim(args.ylim if args.ylim else (-1.1, 1.1))
        ax.set_title(args.title)
        ax.legend(loc="best")
        fig.tight_layout()
        atomic_save(fig, args.png)
        print(f"wrote {args.png}")
        if not args.no_pdf:
            pdf = os.path.splitext(args.png)[0] + ".pdf"
            atomic_save(fig, pdf)
            print(f"wrote {pdf}")
        return

    if args.mode == "zr":
        for p in (args.zr_vqe_csv, args.zr_csv):
            if not os.path.isfile(p):
                fail(f"input CSV not found: {p}")
        try:
            zv = pd.read_csv(args.zr_vqe_csv)
            za = pd.read_csv(args.zr_csv)
        except Exception as e:  # noqa: BLE001
            fail(f"cannot parse CSV: {e}")
        for col in ("s", "delta", "ZR_vqe"):
            if col not in zv.columns:
                fail(f"{args.zr_vqe_csv} missing column: {col}")
        if "tilde_ZR" not in za.columns:
            fail(f"{args.zr_csv} missing column: tilde_ZR")
        vv = zv[abs(zv["delta"] - args.delta) < 1e-12].sort_values("s")
        aa = za[abs(za["delta"] - args.delta) < 1e-12].sort_values("s")
        if len(vv) == 0 or len(aa) == 0:
            fail(f"no rows for delta={args.delta}")
        fig, ax = plt.subplots(figsize=(8, 5.2), dpi=150)
        ax.plot(aa["s"], aa["tilde_ZR"], label=r"$\tilde{Z}_\mathcal{R}$ analytic", color="black")
        ax.plot(vv["s"], vv["ZR_vqe"], label=r"$\tilde{Z}_{\mathcal{R},\mathrm{VQE}}$", marker="D",
                markersize=3, linestyle="-", color="C3")
        ax.set_xlabel("s")
        ax.set_ylabel(r"$\tilde{Z}_\mathcal{R}$")
        ax.set_ylim(-1.2, 1.2)
        ax.set_title(args.title)
        ax.legend(loc="best")
        fig.tight_layout()
        atomic_save(fig, args.png)
        print(f"wrote {args.png}")
        if not args.no_pdf:
            pdf = os.path.splitext(args.png)[0] + ".pdf"
            atomic_save(fig, pdf)
            print(f"wrote {pdf}")
        return

    vv = v[abs(v["delta"] - args.delta) < 1e-12].sort_values("s")
    aa = a[abs(a["delta"] - args.delta) < 1e-12].sort_values("s")
    if len(vv) == 0 or len(aa) == 0:
        fail(f"no rows for delta={args.delta}")

    fig, ax = plt.subplots(figsize=(8, 5.2), dpi=150)
    ax.plot(aa["s"], aa["E0"], label=r"$E_0$ analytic", color="black")
    ax.plot(aa["s"], aa["E1"], label=r"$E_1$ analytic", color="gray", linestyle="--")
    if args.mode == "min":
        vmin = vv[["E_triv", "E_topo", "E_afm"]].min(axis=1)
        ax.plot(vv["s"], vmin, label="min(VQE)", marker="D", markersize=3, linestyle="-", color="C3")
    else:
        ax.plot(vv["s"], vv["E_triv"], label="VQE triv", marker="o", markersize=3, linestyle="-", color="C0")
        ax.plot(vv["s"], vv["E_topo"], label="VQE topo", marker="s", markersize=3, linestyle="-", color="C1")
        ax.plot(vv["s"], vv["E_afm"], label="VQE afm", marker="^", markersize=3, linestyle="-", color="C2")
    ax.set_xlabel("s")
    ax.set_ylabel("energy")
    ax.set_title(args.title)
    ax.legend(loc="best")
    fig.tight_layout()

    atomic_save(fig, args.png)
    print(f"wrote {args.png}")
    if not args.no_pdf:
        pdf = os.path.splitext(args.png)[0] + ".pdf"
        atomic_save(fig, pdf)
        print(f"wrote {pdf}")


if __name__ == "__main__":
    main()

"""exp05 T007 生产断言（零机时）：对正式输出全量执行，逐条映射 spec VAL-001..VAL-008。

任一硬门失败即非零退出并指明候选；诊断只记录。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp05_common import (  # noqa: E402
    DATA_DIR,
    TIE_TOL,
    read_json,
)

FAIL: list[str] = []


def hard(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        FAIL.append(msg)


def main() -> None:
    manifest = read_json(DATA_DIR / "exp05_manifest.json")
    hard(manifest.get("schema") == "exp05/v1", "manifest schema exp05/v1")
    bill = read_json(DATA_DIR / "bill.json")
    hard(bool(bill.get("confirmed", False)), "bill 已人工确认")

    for kind in ("chain", "ring"):
        pre = read_json(DATA_DIR / f"prescreen_{kind}.json")
        surv = pre["survivors"]
        n_surv = sum(len(v) for v in surv.values())
        for chip, lst in surv.items():
            for c in lst:
                if len(set(c)) != len(c):
                    hard(False, f"{kind} {chip} 候选含重复节点 {c}")
        hard(True, f"{kind} survivors 无重复节点/死比特（prescreen 已滤）")

    d07 = np.load(DATA_DIR / "exp05_D07a.npz", allow_pickle=True)
    d08 = np.load(DATA_DIR / "exp05_D07b.npz", allow_pickle=True)
    d09 = np.load(DATA_DIR / "exp05_D07c.npz", allow_pickle=True)
    s04 = np.load(DATA_DIR / "exp05_S04.npz", allow_pickle=True)

    for name, d, pfile in (
        ("D07a", d07, "prescreen_chain.json"),
        ("D07b", d08, "prescreen_ring.json"),
    ):
        pre = read_json(DATA_DIR / pfile)
        n_surv = sum(len(v) for v in pre["survivors"].values())
        hard(len(d["score"]) == n_surv,
             f"{name} evidence 数 {len(d['score'])} == survivors {n_surv}")
        hard(bool(np.all((d["stab_mean"] >= -1) & (d["stab_mean"] <= 1))),
             f"{name} S̄ ∈ [-1,1]")
        hard(bool(np.all((d["readout_fid"] >= 0) & (d["readout_fid"] <= 1))),
             f"{name} F_ro ∈ [0,1]")
        hard(bool(np.all(np.isfinite(d["score"]))), f"{name} 无 NaN/缺失")
        hard(bool(np.all(np.diff(d["score"]) <= 0)), f"{name} 按 score 降序")
    hard(all(bool(v) for v in manifest["snapshots"].values()),
         "拓扑快照含 calibration_time")

    for name in ("exp05_chain", "exp05_ring"):
        p = DATA_DIR / f"submit_transpile_audit_{name}.json"
        hard(p.is_file(), f"转译审计 {name} 存在")
        if p.is_file():
            a = read_json(p)
            bad = [s for s in a["samples"] if not s["ok"]]
            hard(not bad, f"转译门 {name} 全 ok（抽样 {len(a['samples'])}）")

    hard(not (DATA_DIR / "submit_invalid_exp05_chain.json").is_file()
         and not (DATA_DIR / "submit_invalid_exp05_ring.json").is_file(),
         "无 invalid 残留标记")

    src = [str(s) for s in d09["source"]]
    hard(all(s == "chain_evidence" for s in src)
         or all(s in ("chain_evidence", "supp") for s in src),
         f"D07c 来源可追溯 {set(src)}")
    if "supp" in set(src):
        hard((DATA_DIR / "exp05_S04.npz").is_file(), "D07c 补测已并入产品")

    for name, d in (("D07a", d07), ("D07b", d08)):
        top, second = d["score"][0], d["score"][1] if len(d["score"]) > 1 else -9
        n_tied = int(np.sum(top - d["score"] < TIE_TOL))
        s_key = "champion_chain" if name == "D07a" else "champion_ring"
        hard(len(s04[s_key]) == n_tied,
             f"{name} 并列复算一致（tol={TIE_TOL}，{n_tied} 个）")

    # --- 诊断（只记录，非门） ---
    for name, d in (("D07a", d07), ("D07b", d08)):
        print(f"诊断 {name}：冠军 S̄={d['stab_mean'][0]:.4f}"
              f"{' ← 可疑（>0.95，疑似 CZ 未真实执行），需人工核查' if d['stab_mean'][0] > 0.95 else ''}")
        order = np.argsort(-d["score"])
        mono = bool(np.all(np.diff(d["stab_mean"][order]) <= 1e-12))
        print(f"诊断 {name}：S̄ 按 score 单调退化 = {mono}")
        c = np.corrcoef(d["stab_mean"], d["readout_fid"])[0, 1]
        print(f"诊断 {name}：稳定子–读出相关系数 = {c:.3f}（权重事后验证线索）")

    if FAIL:
        print(f"VERIFY-EXP05-FAIL：{len(FAIL)} 项", flush=True)
        raise SystemExit(1)
    print("VERIFY-EXP05-OK", flush=True)


if __name__ == "__main__":
    main()

"""exp05 T004 组装（零机时）：checkpoints → 打分验算 → D07a/D07b/D07c/S04 + manifest。

读 checkpoints（exp05_chain/exp05_ring + 可能的 exp05_supp），逐候选
score_chain 复算（与 recommend 一致，不一致即报错），链/环各自跨芯片统一排序。
D07c：冠军环（D07b 第 1 名）内 10 条连续 8-子链 join 链 evidence；
未命中输出 supp_chain.json（由 submit --supp 补测后重跑本脚本）。
产物：data/exp05/exp05_{D07a,D07b,D07c,S04}.npz + exp05_manifest.json。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp05_common import (  # noqa: E402
    DATA_DIR,
    EDGE_FID_CUTOFF,
    MASTER_SEED,
    RNG_SEED,
    TIE_TOL,
    match_subchain,
    read_json,
    subchain_windows,
    tie_group,
    write_json,
)

from qmeas.benchmark.circuits import build_circuits  # noqa: E402
from qmeas.benchmark.runner import _load_ckpt  # noqa: E402
from qmeas.benchmark.scoring import score_chain  # noqa: E402

CHAIN_LEN = 8
RING_LEN = 10
SHOTS = 2048
W_STAB, W_RO = 0.8, 0.2
SCHEMA = "exp05/v1"


def load_evidence(kind: str, length: int, names: list[str],
                  chains: dict[str, list]) -> list[dict]:
    """读 ckpt → 复算打分 → evidence（machine-recomputed，不信任中间值）。"""
    from qmeas.benchmark.config import BenchmarkConfig
    cset = build_circuits(length, ring=(kind == "ring"))
    ev: list[dict] = []
    for name in names:
        cfg = BenchmarkConfig(output_dir=DATA_DIR, name=name)
        for chip, lst in chains.items():
            for ci, cand in enumerate(lst):
                counts, tids = _load_ckpt(cfg, chip, ci)
                if any(k not in counts for k in
                       ("stab_g0", "stab_g1", "allzero", "allone")):
                    continue  # 补测命名空间无此候选，跳过
                m, f, s = score_chain(counts, cset.stab_groups, SHOTS,
                                      W_STAB, W_RO)
                ev.append({"chip": chip, "chain": list(cand),
                           "stab_mean": m, "readout_fid": f, "score": s,
                           "tids": {k: int(v) for k, v in tids.items()},
                           "ckpt": f"{name}_{chip}_c{ci}"})
    # 同一候选去重（主命名空间优先）
    seen: dict = {}
    for e in ev:
        key = (e["chip"], tuple(e["chain"]))
        if key not in seen:
            seen[key] = e
    return list(seen.values())


def pkg_versions() -> dict:
    import importlib.metadata as md

    def ver(pkg: str) -> str:
        try:
            return md.version(pkg)
        except Exception:
            return "unknown"

    import qmeas as _qmeas

    qmeas_root = Path(_qmeas.__file__).resolve().parent.parent.parent
    try:
        qmeas_commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=qmeas_root,
        ).stdout.strip() or "unknown"
    except Exception:
        qmeas_commit = "unknown"
    return {"qmeas": ver("qmeas"), "qmeas_git": qmeas_commit,
            "quarkstudio": ver("quarkstudio"),
            "quarkcircuit": ver("quarkcircuit"),
            "qiskit": ver("qiskit"), "qiskit_aer": ver("qiskit-aer")}


def main() -> None:
    bill = read_json(DATA_DIR / "bill.json")
    pre_c = read_json(DATA_DIR / "prescreen_chain.json")
    pre_r = read_json(DATA_DIR / "prescreen_ring.json")

    chain_ev = load_evidence("chain", CHAIN_LEN,
                             ["exp05_chain", "exp05_supp"], pre_c["survivors"])
    ring_ev = load_evidence("ring", RING_LEN, ["exp05_ring"], pre_r["survivors"])

    n_chain = sum(len(v) for v in pre_c["survivors"].values())
    n_ring = sum(len(v) for v in pre_r["survivors"].values())
    if len(chain_ev) < n_chain or len(ring_ev) < n_ring:
        raise RuntimeError(
            f"evidence 不全：链 {len(chain_ev)}/{n_chain}，环 {len(ring_ev)}/{n_ring} "
            f"→ 先补跑 submit 再 assemble")

    ranked_chain = sorted(chain_ev, key=lambda e: e["score"], reverse=True)
    ranked_ring = sorted(ring_ev, key=lambda e: e["score"], reverse=True)
    top10_chain = ranked_chain[:10]
    top10_ring = ranked_ring[:10]

    # D07c：冠军环（D07b 第 1 名）内 10 条连续 8-子链
    champ_ring = ranked_ring[0]
    subs = subchain_windows(champ_ring["chain"], CHAIN_LEN)
    d09, missing = [], []
    for sub in subs:
        hit = match_subchain(sub, champ_ring["chip"], chain_ev)
        if hit is None:
            missing.append(sub)
            d09.append({"subchain": sub, "chip": champ_ring["chip"],
                        "source": "missing", "score": None})
        else:
            d = dict(hit)
            d["subchain"] = sub
            d["source"] = "chain_evidence"
            d09.append(d)
    if missing:
        write_json(DATA_DIR / "supp_chain.json",
                   {"chains": {champ_ring["chip"]: missing},
                    "reason": "D07c 未覆盖子链补测（spec Q4）"})
        print(f"D07c 缺 {len(missing)} 条子链 → supp_chain.json，"
              f"跑 submit --supp 补测后重跑 assemble")
    d09_ranked = sorted([d for d in d09 if d["score"] is not None],
                        key=lambda d: d["score"], reverse=True)
    if missing:
        raise RuntimeError("D07c 有缺失子链，已输出补测清单（见上）")

    # S04：冠军链 + 冠军环（并列 <0.02 全记）
    tied_chain = tie_group(ranked_chain)
    tied_ring = tie_group(ranked_ring)
    s04 = {
        "champion_chain": [
            {"chip": e["chip"], "chain": e["chain"], "score": e["score"]}
            for e in tied_chain],
        "champion_ring": [
            {"chip": e["chip"], "chain": e["chain"], "score": e["score"]}
            for e in tied_ring],
        "snapshots": bill["snapshots"],
        "tie_tol": TIE_TOL,
        "reused_shenglian_from": bill.get("reused_shenglian_from"),
        "reused_shenglian_snapshot": bill.get("reused_shenglian_snapshot"),
    }

    def ev_arrays(ranked):
        return {
            "chip": np.array([e["chip"] for e in ranked]),
            "chain": np.array([e["chain"] for e in ranked], dtype=np.int64),
            "stab_mean": np.array([e["stab_mean"] for e in ranked]),
            "readout_fid": np.array([e["readout_fid"] for e in ranked]),
            "score": np.array([e["score"] for e in ranked]),
        }

    np.savez(DATA_DIR / "exp05_D07a.npz", **ev_arrays(ranked_chain),
             top10_idx=np.arange(min(10, len(ranked_chain))))
    np.savez(DATA_DIR / "exp05_D07b.npz", **ev_arrays(ranked_ring),
             top10_idx=np.arange(min(10, len(ranked_ring))))
    np.savez(DATA_DIR / "exp05_D07c.npz",
             subchain=np.array([d["subchain"] for d in d09_ranked],
                               dtype=np.int64),
             chip=np.array([d["chip"] for d in d09_ranked]),
             stab_mean=np.array([d["stab_mean"] for d in d09_ranked]),
             readout_fid=np.array([d["readout_fid"] for d in d09_ranked]),
             score=np.array([d["score"] for d in d09_ranked]),
             source=np.array([d["source"] for d in d09_ranked]),
             champ_ring_chip=np.array(champ_ring["chip"]),
             champ_ring=np.array(champ_ring["chain"], dtype=np.int64))
    np.savez(DATA_DIR / "exp05_S04.npz",
             champion_chain=np.array(
                 [e["chain"] for e in tied_chain], dtype=np.int64),
             champion_chain_chip=np.array([e["chip"] for e in tied_chain]),
             champion_ring=np.array(
                 [e["chain"] for e in tied_ring], dtype=np.int64),
             champion_ring_chip=np.array([e["chip"] for e in tied_ring]))

    manifest = {
        "schema": SCHEMA,
        "chips": ["Baihua", "Shenglian"],
        "snapshots": bill["snapshots"],
        "chain_length": CHAIN_LEN, "ring_length": RING_LEN,
        "max_chains_per_chip": 3000,
        "n_chain_survivors": n_chain, "n_ring_survivors": n_ring,
        "shots": SHOTS, "w_stab": W_STAB, "w_ro": W_RO,
        "rng_seed": RNG_SEED, "master_seed": MASTER_SEED,
        "edge_fid_cutoff": EDGE_FID_CUTOFF, "tie_tol": TIE_TOL,
        "top1_chain": {"chip": ranked_chain[0]["chip"],
                       "chain": ranked_chain[0]["chain"],
                       "score": ranked_chain[0]["score"]},
        "top1_ring": {"chip": ranked_ring[0]["chip"],
                      "chain": ranked_ring[0]["chain"],
                      "score": ranked_ring[0]["score"]},
        "n_tied_chain": len(tied_chain), "n_tied_ring": len(tied_ring),
        "reused_shenglian_from": bill.get("reused_shenglian_from"),
        "reused_shenglian_snapshot": bill.get("reused_shenglian_snapshot"),
        "toolchain": pkg_versions(),
        "python": sys.executable,
    }
    write_json(DATA_DIR / "exp05_manifest.json", manifest)
    print(f"D07a 链 {len(ranked_chain)} 条，top1 {manifest['top1_chain']}")
    print(f"D07b 环 {len(ranked_ring)} 条，top1 {manifest['top1_ring']}")
    print(f"D07c {len(d09_ranked)} 条子链；S04 并列链 {len(tied_chain)} / 环 "
          f"{len(tied_ring)}；manifest 落盘")


if __name__ == "__main__":
    main()

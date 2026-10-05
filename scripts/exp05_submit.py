"""exp05 T003 真机提交（烧机时）：转译抽样断言 → 提交 → 对账 → 缺失补跑。

必须用 qmeas env python 运行，且 bill.json confirmed=true（人工确认）后才执行：
  $QPY scripts/exp05_submit.py [--supp]

--supp：只补跑 D07c 缺失子链（读 supp_chain.json，独立 ckpt 命名空间 exp05_supp）。
对账层（exp05 侧，不改 qmeas）：ckpt 扫描 → 缺失补跑（≤2 轮）→ 仍缺失判 invalid。
中断续跑只补缺失：已有 tid 只轮询不重提（内核保证），已收回永不重提。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp05_common import (  # noqa: E402
    DATA_DIR,
    read_json,
    write_json,
)

from qmeas.benchmark.circuits import build_circuits  # noqa: E402
from qmeas.benchmark.config import BenchmarkConfig  # noqa: E402
from qmeas.benchmark.runner import (  # noqa: E402
    _load_ckpt,
    run_benchmark,
)

CHAIN_LEN = 8
RING_LEN = 10
CIRCUIT_KEYS = ("stab_g0", "stab_g1", "allzero", "allone")
MAX_AUDIT_ROUNDS = 2
TRANSPILE_SAMPLE = 5


def make_config(shape: str, length: int, name: str) -> BenchmarkConfig:
    return BenchmarkConfig(
        chips=["Baihua", "Shenglian"],
        chain_length=length,
        max_chains_per_chip=3000,
        shots=2048,
        w_stab=0.8,
        w_ro=0.2,
        expansion="sample",
        shape=shape,
        output_dir=DATA_DIR,
        name=name,
    )


def transpile_audit(chains: dict[str, list], cset, ring: bool,
                    opt_level: int) -> dict:
    """抽样转译断言：CZ 数 == 候选边数且比特集 ⊆ 候选（spec 转译门）。"""
    from qiskit import transpile

    n0 = len(next(iter(next(iter(chains.values())))))
    want_cz = n0 if ring else n0 - 1
    audit: dict = {"optimization_level": opt_level, "want_cz": want_cz,
                   "samples": []}
    for chip, lst in chains.items():
        idx = [0, len(lst) // 2, -1][:min(3, len(lst))]
        extra = [i for i in range(0, len(lst), max(1, len(lst) // TRANSPILE_SAMPLE))
                 if i not in idx][:TRANSPILE_SAMPLE]
        for ci in sorted(set(idx) | set(extra)):
            chain = lst[ci]
            n = len(chain)
            edges = [[i, i + 1] for i in range(n - 1)]
            if ring:
                edges.append([n - 1, 0])
            # 只断言含 CZ 的 stab 电路；allzero/allone 依定义不含 CZ（spec POST-002）。
            for key in ("stab_g0", "stab_g1"):
                t = transpile(cset.circuits[key],
                              basis_gates=["rz", "rx", "ry", "cz"],
                              optimization_level=opt_level,
                              coupling_map=edges)
                n_cz = t.count_ops().get("cz", 0)
                qubits = set()
                for inst in t.data:
                    qs = [t.find_bit(q).index for q in inst.qubits]
                    if inst.operation.name == "cz":
                        qubits.update(qs)
                ok = (n_cz == want_cz) and qubits <= set(range(n))
                audit["samples"].append(
                    {"chip": chip, "ci": ci, "circuit": key,
                     "n_cz": n_cz, "ok": ok})
                if not ok:
                    raise RuntimeError(
                        f"转译断言失败 {chip} c{ci} {key}: cz={n_cz} "
                        f"want={want_cz} qubits={sorted(qubits)}")
    return audit


def audit_checkpoints(cfg: BenchmarkConfig,
                      chains: dict[str, list]) -> dict[str, list]:
    """扫描 ckpt：返回 {chip: [缺失 ci]}（任一电路无计数即缺失）。"""
    missing: dict[str, list] = {}
    for chip, lst in chains.items():
        for ci in range(len(lst)):
            counts, _ = _load_ckpt(cfg, chip, ci)
            if any(k not in counts for k in CIRCUIT_KEYS):
                missing.setdefault(chip, []).append(ci)
    return missing


def run_shape(shape: str, length: int, chains: dict[str, list],
              name: str) -> None:
    cfg = make_config(shape, length, name)
    cset = build_circuits(length, ring=(shape == "ring"))
    audit = transpile_audit(chains, cset, ring=(shape == "ring"),
                            opt_level=cfg.runner_opts.optimization_level)
    write_json(DATA_DIR / f"submit_transpile_audit_{name}.json", audit)
    print(f"转译抽样断言通过（{len(audit['samples'])} 样本），开始提交 {name}",
          flush=True)
    asyncio.run(run_benchmark(cfg, chains))
    for rnd in range(1 + MAX_AUDIT_ROUNDS):
        missing = audit_checkpoints(cfg, chains)
        nmiss = sum(len(v) for v in missing.values())
        if nmiss == 0:
            print(f"{name} 对账通过：全收回", flush=True)
            return
        print(f"{name} 对账第 {rnd} 轮：缺失 {nmiss} 候选 → 补跑", flush=True)
        if rnd < MAX_AUDIT_ROUNDS:
            asyncio.run(run_benchmark(cfg, chains))
    missing = audit_checkpoints(cfg, chains)
    write_json(DATA_DIR / f"submit_invalid_{name}.json", missing)
    raise RuntimeError(f"{name} 补跑 {MAX_AUDIT_ROUNDS} 轮后仍缺失：{missing} "
                       f"→ 判 invalid（见 submit_invalid_{name}.json）")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp", action="store_true", help="只补跑 D07c 缺失子链")
    ap.add_argument("--reuse-shenglian-from", default=None,
                    help="拷贝上轮 Shenglian 链 checkpoints，免重提交 "
                         "(如 data/exp05_run1_20261003)")
    args = ap.parse_args()

    bill = read_json(DATA_DIR / "bill.json")
    if not bill.get("confirmed", False):
        raise RuntimeError("bill.json confirmed=false：须人工确认账单后才可提交")

    if args.supp:
        supp = read_json(DATA_DIR / "supp_chain.json")
        run_shape("chain", CHAIN_LEN, supp["chains"], "exp05_supp")
        return

    if args.reuse_shenglian_from:
        import shutil
        from pathlib import Path as _P
        src = _P(args.reuse_shenglian_from) / "checkpoints"
        dst = DATA_DIR / "checkpoints"
        dst.mkdir(parents=True, exist_ok=True)
        n = 0
        for p in sorted(src.glob("exp05_chain_Shenglian_*.json")):
            # 顺序与 survivors 一致（prescreen 复用已保证），直接拷贝；
            # run_benchmark 续跑机制自动跳过已收回者。
            shutil.copy2(p, dst / p.name)
            n += 1
        print(f"复用上轮 Shenglian 链 checkpoints {n} 份（免重提交）", flush=True)

    pre_c = read_json(DATA_DIR / "prescreen_chain.json")["survivors"]
    pre_r = read_json(DATA_DIR / "prescreen_ring.json")["survivors"]
    run_shape("chain", CHAIN_LEN, pre_c, "exp05_chain")
    run_shape("ring", RING_LEN, pre_r, "exp05_ring")


if __name__ == "__main__":
    main()

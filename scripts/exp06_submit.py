"""exp06 T003 真机提交（烧机时）：转译 → 逐批提交 → 对账补跑。

必须用 qmeas env python 运行，且 bill.json confirmed=true 后才执行。
逐批任务 = 3 组 × 5 重复 VQE + 2 标定（同批）；correct=False 参数留存。
转译用逻辑 coupling_map（开链 7 边 / 环 8 边含 0–7），qasm qubit i ↔
target_qubits[i]；物理侧 0–7 跳由平台路由（spec link 语义）。
转译后 CZ 边集随 batch 落盘，供 verify 验路断言（须 ⊆ 允许集）。
中断续跑只补缺失：已有 tid 只轮询不重提。
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, qasm2, transpile

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp06_circuits import (  # noqa: E402
    L,
    build_calib_circuits,
    build_estimator_circuit,
)
from exp06_common import (  # noqa: E402
    DATA_DIR,
    REPS,
    SHOTS,
    read_json,
    write_json,
)

BASIS_GATES = ["rz", "rx", "ry", "cz"]
OPT_LEVEL = 3
MAX_AUDIT_ROUNDS = 2
N_TASKS_PER_BATCH = 3 * REPS + 2


def logical_edges(a_star: int) -> list:
    edges = [[i, i + 1] for i in range(L - 1)]
    if a_star == 2:  # topo：0–7 闭合边（link 语义，spec §3）
        edges.append([0, L - 1])
    return edges


def allowed_edges(a_star: int) -> set:
    base = {(i, i + 1) for i in range(L - 1)}
    if a_star == 2:
        base.add((0, L - 1))
    return base


def cz_edges(tqc) -> set:
    out = set()
    for inst in tqc.data:
        if inst.operation.name == "cz":
            qs = sorted(tqc.find_bit(q).index for q in inst.qubits)
            out.add(tuple(qs))
    return out


def build_batch_tasks(batch, theta_map, phys_map) -> dict[str, QuantumCircuit]:
    """批内全部逻辑电路：{task_key: circuit}（不转译）。"""
    circuits: dict[str, QuantumCircuit] = {}
    for gi, g in enumerate(batch):
        key = (g["delta_idx"], g["s_idx"], g["p"])
        th, a = theta_map[key]
        for r in range(REPS):
            circuits[f"g{gi}_rep{r}"] = build_estimator_circuit(
                th, a, g["p"], g["delta"])
    circuits.update(build_calib_circuits())
    return circuits


async def run_batch(bid: int, batch: list[dict], theta_map: dict,
                    phys_map: dict) -> None:
    from qmeas.random.quark_client import (
        await_quark,
        make_quark_task,
        quark_token,
        submit_quark,
    )
    from qmeas.random.config import QuarkOptions

    bdir = DATA_DIR / "batches" / f"{bid:03d}"
    bdir.mkdir(parents=True, exist_ok=True)
    base_opts = QuarkOptions(chip="Baihua", mitigation=False, correct=False,
                             optimization_level=OPT_LEVEL,
                             basis_gates=list(BASIS_GATES))
    assert base_opts.correct is False  # T000：平台矫正确保关闭
    token = quark_token(base_opts)
    tmgr = make_quark_task(token, base_opts.submit_retries)

    circuits = build_batch_tasks(batch, theta_map, phys_map)
    # 每任务物理映射：VQE 按 a*（开链 top1 / 环内最优子链），标定跟首组。
    task_phys: dict[str, list[int]] = {}
    task_a: dict[str, int] = {}
    for gi, g in enumerate(batch):
        for r in range(REPS):
            task_phys[f"g{gi}_rep{r}"] = phys_map[g["a_star"]]
            task_a[f"g{gi}_rep{r}"] = g["a_star"]
    first_a = batch[0]["a_star"]
    for k in ("cal_zero", "cal_one"):
        task_phys[k] = phys_map[first_a]
        task_a[k] = first_a

    state_path = bdir / "state.json"
    if state_path.is_file():
        state = read_json(state_path)
    else:
        state = {"tids": {}, "counts": {}, "transpile": {}, "submit_params": {}}

    # 转译（缺失才做）+ 验路断言数据留存。
    for key, qc in circuits.items():
        if key not in state["transpile"]:
            t = transpile(qc, basis_gates=BASIS_GATES,
                          optimization_level=OPT_LEVEL,
                          coupling_map=logical_edges(task_a[key]))
            edges = sorted(cz_edges(t))
            state["transpile"][key] = {
                "cz_edges": edges, "a_star": task_a[key],
                "in_allowed": all(tuple(e) in allowed_edges(task_a[key])
                                  for e in edges)}
            state["submit_params"][key] = {
                "chip": "Baihua", "shots": SHOTS, "correct": False,
                "optimization_level": OPT_LEVEL,
                "basis_gates": BASIS_GATES,
                "target_qubits": task_phys[key]}
            write_json(state_path, state)

    sem_sub = asyncio.Semaphore(base_opts.max_submit_concurrency)
    sem_poll = asyncio.Semaphore(base_opts.max_poll_concurrency)

    async def submit_one(key):
        async with sem_sub:
            opts = replace(base_opts, chip="Baihua",
                           target_qubits=task_phys[key],
                           coupling_map=None)
            t = transpile(circuits[key], basis_gates=BASIS_GATES,
                          optimization_level=OPT_LEVEL,
                          coupling_map=logical_edges(task_a[key]))
            qasm = qasm2.dumps(t)
            tid = await asyncio.to_thread(
                submit_quark, tmgr, opts, qasm, SHOTS, f"exp06_b{bid:03d}_{key}")
            return key, int(tid)

    async def poll_one(key, tid):
        async with sem_poll:
            opts = replace(base_opts, chip="Baihua",
                           target_qubits=task_phys[key])
            hist = await await_quark(
                tmgr, tid, opts, sem_sub, "", SHOTS,
                f"exp06_b{bid:03d}_{key}", attempt_tag=f"b{bid:03d}")
            return key, hist

    for rnd in range(1 + MAX_AUDIT_ROUNDS):
        missing_submit = [k for k in circuits if k not in state["tids"]]
        if missing_submit:
            print(f"batch {bid} 第 {rnd} 轮提交 {len(missing_submit)} 任务",
                  flush=True)
            for key, tid in await asyncio.gather(
                    *(submit_one(k) for k in missing_submit)):
                state["tids"][key] = tid
                write_json(state_path, state)
        missing_counts = [k for k in circuits if k not in state["counts"]]
        if not missing_counts:
            print(f"batch {bid} 对账通过：{len(circuits)} 任务全收回", flush=True)
            return
        print(f"batch {bid} 第 {rnd} 轮轮询 {len(missing_counts)} 任务",
              flush=True)
        for key, hist in await asyncio.gather(
                *(poll_one(k, state["tids"][k]) for k in missing_counts)):
            state["counts"][key] = hist
            write_json(state_path, state)
    missing = [k for k in circuits if k not in state["counts"]]
    write_json(bdir / "invalid.json", {"missing": missing})
    raise RuntimeError(f"batch {bid} 补跑后仍缺失 {missing} → 判 invalid")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=None, help="只跑指定批（调试）")
    args = ap.parse_args()
    bill = read_json(DATA_DIR / "bill.json")
    if not bill.get("confirmed", False):
        raise RuntimeError("bill.json confirmed=false：须人工确认账单后才可提交")
    info = read_json(DATA_DIR / "batches.json")
    s03 = np.load(DATA_DIR.parent / "exp04" / "exp04_S03.npz")
    meta, th = s03["meta"], s03["theta"]
    theta_map: dict = {}
    for r in range(len(meta)):
        di, si, p, a = (int(v) for v in meta[r])
        npl = 4 if di == 1 else 8
        theta_map[(di, si, p)] = (th[r][:npl * p], a)
    phys_map = {1: info["chain_top1"], 3: info["chain_top1"],
                2: info["subchain_top1"]}
    bids = [args.batch] if args.batch is not None else range(len(info["batches"]))
    for bid in bids:
        asyncio.run(run_batch(bid, info["batches"][bid], theta_map, phys_map))


if __name__ == "__main__":
    main()

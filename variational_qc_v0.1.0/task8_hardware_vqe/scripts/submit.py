#!/usr/bin/env python
"""task8 真机提交：612 点 × X/Y/Z 三基一次全交，统一轮询。

前置：账单已人工确认。两阶段（转译限流16 → 提交信号量10 → tids 即时落盘
→ 轮询50并发逐个落盘）；中断重跑有 tid 只轮询不重提。
读出纠错开（correct=True）。

运行（项目根）：
  export QUARK_TOKEN=...
  $QPY task8_hardware_vqe/scripts/submit.py
"""

import asyncio
import json
import tomllib
from dataclasses import replace
from pathlib import Path

from qiskit import qasm2, transpile

HERE = Path(__file__).resolve()
TASK8 = HERE.parent.parent
ROOT = TASK8.parent
import sys
sys.path.insert(0, str(TASK8 / "scripts"))

from circuits import build_prep, measure_circuit, coupling_for  # noqa: E402

from qmeas.benchmark.runner import _guard_empty_qubits  # noqa: E402
from qmeas.random import QuarkOptions  # noqa: E402
from qmeas.random.quark_client import (  # noqa: E402
    await_quark,
    make_quark_task,
    quark_token,
    submit_quark,
)

BASES = ("X", "Y", "Z")
SHOTS = 1024


def load_grid():
    with open(TASK8 / "config" / "grid.toml", "rb") as f:
        return tomllib.load(f)


def winner_theta(th, delta, s, init):
    key = f"{round(float(delta), 8)}|{round(float(s), 8)}|{init}"
    seeds = th[key]["seeds"]
    return min(seeds, key=lambda r: r["fun"])["x"]


def ckpt_path(name):
    return TASK8 / "data" / "checkpoints" / f"{name}.json"


def load_ckpt(name):
    p = ckpt_path(name)
    if not p.is_file():
        return {}, {}
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("counts", {}), d.get("tids", {})


def save_ckpt(name, meta, counts, tids):
    p = ckpt_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(
        {"meta": meta, "counts": counts, "tids": tids},
        ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


def transpile_qasm(qc, opts):
    basic = transpile(
        qc,
        basis_gates=opts.basis_gates,
        optimization_level=opts.optimization_level,
        coupling_map=opts.coupling_map,
    )
    return qasm2.dumps(_guard_empty_qubits(basic))


async def main() -> None:
    g = load_grid()
    chain = g["mapping"]["chain"]
    ring10 = g["mapping"]["ring10"]
    th = {
        "sym": json.load(open(ROOT / g["thetas"]["sym"], encoding="utf-8")),
        "nosym": json.load(open(ROOT / g["thetas"]["nosym"], encoding="utf-8")),
    }
    import numpy as np
    ss = list(np.linspace(g["grid"]["s_min"], g["grid"]["s_max"],
                          g["grid"]["ns"]))
    base_opts = QuarkOptions(
        chip="Baihua",
        target_qubits=[],
        mitigation=False,
        coupling_map=None,
        optimization_level=3,
        basis_gates=["rz", "rx", "ry", "cz"],
        correct=True,  # 读出纠错开
        max_submit_concurrency=10,
        max_poll_concurrency=50,
    )
    token = quark_token(base_opts)
    tmgr = make_quark_task(token, base_opts.submit_retries)
    submit_sem = asyncio.Semaphore(base_opts.max_submit_concurrency)
    poll_sem = asyncio.Semaphore(base_opts.max_poll_concurrency)
    transpile_sem = asyncio.Semaphore(4)  # O3 转译吃内存（11G 机），限 4 防 OOM

    jobs = []
    for task in ("sym", "nosym"):
        for init in ("triv", "topo", "afm"):
            is_ring = task == "sym" and init == "topo"
            mapping = ring10 if is_ring else chain
            for delta in g["grid"]["deltas"]:
                for s in ss:
                    theta = winner_theta(th[task], delta, float(s), init)
                    prep = build_prep(task, init, theta)
                    name = (f"task8_hwvqe_{task}_{init}_"
                            f"d{delta}_s{float(s):.4f}")
                    opts = replace(
                        base_opts, chip="Baihua", target_qubits=list(mapping),
                        coupling_map=coupling_for(task, init))
                    counts, tids = load_ckpt(name)
                    missing = [b for b in BASES if b not in counts]
                    to_submit = [b for b in missing if b not in tids]
                    jobs.append({
                        "name": name, "opts": opts,
                        "meta": {"task": task, "init": init,
                                 "delta": delta, "s": float(s),
                                 "theta": [float(t) for t in theta]},
                        "counts": counts, "tids": tids,
                        "missing": missing, "to_submit": to_submit,
                        "qasms": {}, "circuits": {
                            b: measure_circuit(prep, b) for b in to_submit},
                    })
    print(f"共 {len(jobs)} 点，待提交 {sum(len(j['to_submit']) for j in jobs)} 电路",
          flush=True)

    async def _tr(job, b):
        async with transpile_sem:
            return await asyncio.to_thread(
                transpile_qasm, job["circuits"][b], job["opts"])

    t_tasks = [asyncio.create_task(_tr(j, b))
               for j in jobs for b in j["to_submit"]]
    if t_tasks:
        out = await asyncio.gather(*t_tasks)
        it = iter(out)
        for j in jobs:
            for b in j["to_submit"]:
                j["qasms"][b] = next(it)
        print("转译完毕", flush=True)

    async def _sub(job, b):
        async with submit_sem:
            return await asyncio.to_thread(
                submit_quark, tmgr, job["opts"], job["qasms"][b],
                SHOTS, f"{job['name']}_{b}")

    s_tasks = [asyncio.create_task(_sub(j, b))
               for j in jobs for b in j["to_submit"]]
    if s_tasks:
        print(f"提交开始，共 {len(s_tasks)} 个任务", flush=True)
        got = await asyncio.gather(*s_tasks)
        it = iter(got)
        for j in jobs:
            for b in j["to_submit"]:
                j["tids"][b] = next(it)
            save_ckpt(j["name"], j["meta"], j["counts"], j["tids"])
        print("提交完毕，tids 已落盘，转入统一轮询", flush=True)

    async def _poll(job, b):
        async with poll_sem:
            hist = await await_quark(
                tmgr, job["tids"][b], job["opts"], submit_sem,
                job["qasms"].get(b, ""), SHOTS, f"{job['name']}_{b}",
                attempt_tag=job["name"])
            return id(job), b, hist

    by_id = {id(j): j for j in jobs}
    p_tasks = [asyncio.create_task(_poll(j, b))
               for j in jobs for b in j["missing"]]
    try:
        for coro in asyncio.as_completed(p_tasks):
            jid, b, hist = await coro
            job = by_id[jid]
            job["counts"][b] = hist
            save_ckpt(job["name"], job["meta"], job["counts"], job["tids"])
    except Exception:
        for t in p_tasks:
            t.cancel()
        raise
    print(f"收回 {len(jobs)} 点结果", flush=True)


if __name__ == "__main__":
    asyncio.run(main())

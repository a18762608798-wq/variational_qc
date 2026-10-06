"""exp05 校准轮询：每 30 分钟由外层 loop 调用一次（零机时）。

对比基线 data/exp05_run1_20261003/bill.json 的 calibration_time，
Baihua 出现新值且连续 2 次一致才判 DONE_STABLE（防校准中途瞬态值）。
Shenglian 仅记录，供 preview 是否 --reuse-shenglian-from 决策。

退出码：0=继续等，1=首次进入 DONE（loop 据此自动跑 preview 后退出），2=本轮异常（loop 继续）。
状态：data/exp05_watch/state.json；日志：data/exp05_watch/watch.log。
必须用 qmeas env python 运行（见 scripts/exp05_watch_loop.sh）。
"""

from __future__ import annotations

import json
import os
import signal
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

PROJ = Path(__file__).resolve().parent.parent
RUN1_BILL = PROJ / "data" / "exp05_run1_20261003" / "bill.json"
WATCH_DIR = PROJ / "data" / "exp05_watch"
STATE = WATCH_DIR / "state.json"
LOG = WATCH_DIR / "watch.log"

CHIPS = ["Baihua", "Shenglian"]
STABLE_HITS = 2  # 连续几次相同新值才算稳定（30min 间隔，2 次 = 约 1h 确认）


def now_cst() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")


def log_line(msg: str) -> None:
    WATCH_DIR.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{now_cst()}] {msg}\n")
    print(msg, flush=True)


def load_state() -> dict:
    if STATE.is_file():
        try:
            s = json.loads(STATE.read_text(encoding="utf-8"))
            # 兼容旧格式 {candidate/hits} → 联合 (b,s) 格式
            if "candidate" in s and "candidate_b" not in s:
                s = {"candidate_b": s.get("candidate"), "candidate_s": None,
                     "hits": int(s.get("hits", 0)), "done": bool(s.get("done", False)),
                     "done_snapshot": s.get("done_snapshot")}
            return s
        except Exception:
            pass
    return {"candidate_b": None, "candidate_s": None, "hits": 0,
            "done": False, "done_snapshot": None}


def save_state(s: dict) -> None:
    WATCH_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE)


def main() -> int:
    # 用户手动停止：直接退出轮询（loop 侧见 STOP 跳过 preview 逻辑）。
    # 先给父进程发 SIGTERM（当前运行中的 loop 立刻退出，不跑 preview）；
    # 若送达失败则返回 1 + done=true，靠 loop 的 DONE-break 兜底退出。
    if (WATCH_DIR / "STOP").exists():
        save_state({"candidate_b": None, "candidate_s": None, "hits": 0,
                    "done": True, "done_snapshot": "STOPPED_BY_USER"})
        log_line("STOP 收到，后台轮询退出（用户手动停止）")
        try:
            os.kill(os.getppid(), signal.SIGTERM)
        except Exception as e:
            log_line(f"父进程信号未送达，走 DONE-break 兜底: {e!r}")
        return 1

    baseline = json.loads(RUN1_BILL.read_text(encoding="utf-8"))["snapshots"]
    base_b = baseline["Baihua"]
    base_s = baseline["Shenglian"]

    from qmeas.benchmark.config import BenchmarkConfig
    from qmeas.benchmark.topology import fetch_topology

    cfg = BenchmarkConfig(
        chips=list(CHIPS),
        chain_length=8,
        max_chains_per_chip=3000,
        shots=2048,
        w_stab=0.8,
        w_ro=0.2,
        expansion="sample",
        shape="chain",
        output_dir=WATCH_DIR / "topo_probe",
    )
    snaps: dict[str, str] = {}
    try:
        for chip in CHIPS:
            info = fetch_topology(cfg, chip, force=True)
            snaps[chip] = info.get("calibration_time", "unknown")
    except Exception as e:
        log_line(f"ERROR 拉取失败（继续等）: {type(e).__name__}: {str(e)[:300]}")
        return 2

    b, s = snaps["Baihua"], snaps["Shenglian"]
    st = load_state()
    if st.get("done"):
        log_line(f"ALREADY_DONE Baihua={b} Shenglian={s} done_snapshot={st.get('done_snapshot')}")
        return 1

    if b == base_b:
        st.update({"candidate_b": None, "candidate_s": None, "hits": 0})
        save_state(st)
        log_line(f"WAIT_OLD Baihua={b}(=基线) Shenglian={s}(基线{base_s})，校准未出新值，继续等")
        return 0

    # Baihua 已出新值，需 (Baihua,Shenglian) 联合连续稳定（防任一芯片校准中途瞬态值）
    if st.get("candidate_b") != b or st.get("candidate_s") != s:
        st.update({"candidate_b": b, "candidate_s": s, "hits": 1})
        save_state(st)
        log_line(
            f"NEW_UNSTABLE Baihua={b}(基线{base_b}→新值，需联合稳定{STABLE_HITS}次) "
            f"Shenglian={s}(基线{base_s})，30min 后复核"
        )
        return 0

    hits = int(st.get("hits", 1)) + 1
    if hits >= STABLE_HITS:
        st.update({"hits": hits, "done": True, "done_snapshot": b})
        save_state(st)
        reuse = "可用" if s == base_s else "不可用(Shenglian亦变，须全重跑)"
        log_line(
            f"DONE_STABLE Baihua={b} Shenglian={s} 联合连续{hits}次一致，判校准结束；"
            f"复用判定：{reuse}"
        )
        return 1

    st.update({"hits": hits})
    save_state(st)
    log_line(f"NEW_CONFIRMING Baihua={b} Shenglian={s} 第{hits}/{STABLE_HITS}次一致，继续等")
    return 0


if __name__ == "__main__":
    sys.exit(main())

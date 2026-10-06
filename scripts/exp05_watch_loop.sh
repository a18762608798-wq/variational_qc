#!/bin/bash
# exp05 校准监控 loop：每 1800s 跑一次 exp05_watch.py（零机时）。
# DONE 后自动跑 exp05_preview.py（零机时，只产账单，不提交机时），然后退出待人工确认。
# 提交机时仍须人工确认 bill.json 后手动执行 submit（spec 两步闸门，不自动）。
# 用法：nohup bash scripts/exp05_watch_loop.sh >> data/exp05_watch/loop.out 2>&1 & echo $!
set -u
cd "$(dirname "$0")/.."
QPY=/home/mintusr/sync/theory/physics/quant_comp/03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
QSRC=/home/mintusr/sync/theory/physics/quant_comp/03_tools_practice/qmeas/src
export PYTHONPATH="$QSRC:${PYTHONPATH:-}"
INTERVAL=1800
mkdir -p data/exp05_watch
echo "[$(date '+%Y-%m-%d %H:%M:%S')] watch_loop 启动，PID=$$，间隔=${INTERVAL}s" | tee -a data/exp05_watch/loop.out
echo $$ > data/exp05_watch/loop.pid
while true; do
  set +e
  PYTHONPATH="$PYTHONPATH" "$QPY" scripts/exp05_watch.py >> data/exp05_watch/loop.out 2>&1
  code=$?
  set -e
  if [ "$code" -eq 1 ]; then
    # 二次确认确为 DONE（防单轮误触）：state.json done=true
    if grep -q '"done": true' data/exp05_watch/state.json 2>/dev/null; then
      if grep -q '"done_snapshot": "STOPPED_BY_USER"' data/exp05_watch/state.json 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 收到 STOP，跳过 preview，直接退出" | tee -a data/exp05_watch/loop.out
        rm -f data/exp05_watch/loop.pid
        break
      fi
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] 校准 DONE，自动跑 preview（零机时）…" | tee -a data/exp05_watch/loop.out
      # Shenglian 若未变则复用省账单，否则全重跑；watch.py 日志已给出判定，这里自动判断
      BASE_S=$(python3 -c "import json;print(json.load(open('data/exp05_run1_20261003/bill.json'))['snapshots']['Shenglian'])")
      NEW_S=$(python3 -c "import json,glob;fs=sorted(glob.glob('data/exp05_watch/topo_probe/topology_cache/Shenglian_*.json'));print(json.load(open(fs[-1]))['calibration_time'] if fs else 'unknown')")
      if [ "$BASE_S" = "$NEW_S" ]; then
        echo "Shenglian 未变，复用上轮链 survivors" | tee -a data/exp05_watch/loop.out
        PYTHONPATH="$PYTHONPATH" "$QPY" scripts/exp05_preview.py --reuse-shenglian-from data/exp05_run1_20261003 >> data/exp05_watch/loop.out 2>&1
      else
        echo "Shenglian 已变（${BASE_S}→${NEW_S}），全重跑 preview" | tee -a data/exp05_watch/loop.out
        PYTHONPATH="$PYTHONPATH" "$QPY" scripts/exp05_preview.py >> data/exp05_watch/loop.out 2>&1
      fi
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] preview 完成，账单待人工确认 data/exp05/bill.json，loop 退出" | tee -a data/exp05_watch/loop.out
      rm -f data/exp05_watch/loop.pid
      break
    fi
  fi
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 下轮 ${INTERVAL}s 后（code=$code），停 loop：kill $(cat data/exp05_watch/loop.pid 2>/dev/null)" >> data/exp05_watch/loop.out
  sleep "$INTERVAL"
done

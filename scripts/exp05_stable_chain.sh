#!/bin/bash
# exp05 稳定即测链（untracked helper，与 watch_loop 同类，不入库）：
# 等 watch 循环 DONE → 等 preview 落新鲜账单 → prescreen → 置 confirmed →
# submit（烧机时，长时间）。
# 确认门：用户 2026-10-04 明确提前授权“校准稳定即自动测量”，confirmed 标志
# 附授权记录后置 true，不再等人。
# 用法：bash scripts/exp05_stable_chain.sh（以前台或 opencode background 任务起，
# 结束靠退出码通知）。日志：data/exp05_watch/chain.log。
set -u
cd "$(dirname "$0")/.."
QPY=/home/mintusr/sync/theory/physics/quant_comp/03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
QSRC=/home/mintusr/sync/theory/physics/quant_comp/03_tools_practice/qmeas/src
export PYTHONPATH="$QSRC:${PYTHONPATH:-}"
LOG=data/exp05_watch/chain.log
mkdir -p data/exp05_watch
say() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

say "stable_chain 启动：等 watch DONE…"
while true; do
  if [ -f data/exp05_watch/state.json ] \
    && grep -q '"done": true' data/exp05_watch/state.json 2>/dev/null; then
    break
  fi
  sleep 60
done
if grep -q 'STOPPED_BY_USER' data/exp05_watch/state.json 2>/dev/null; then
  say "STOPPED_BY_USER，链路退出不执行"
  exit 0
fi
B=$(python3 -c "import json;print(json.load(open('data/exp05_watch/state.json'))['candidate_b'])")
say "DONE 观测到，候选 Baihua=$B，等 preview 落新鲜账单…"
OK=0
for _ in $(seq 1 80); do
  if [ -f data/exp05/bill.json ]; then
    BB=$(python3 -c "import json;print(json.load(open('data/exp05/bill.json')).get('snapshots',{}).get('Baihua',''))")
    if [ "$BB" = "$B" ]; then OK=1; break; fi
  fi
  sleep 30
done
if [ "$OK" -ne 1 ]; then
  say "ERROR 40min 内无新鲜账单（要 $B），退出等人看"
  exit 1
fi
say "账单新鲜：$(python3 -c "import json;b=json.load(open('data/exp05/bill.json'));print(b['total_tasks'],'任务',b['total_shots'],'shots',b['snapshots'])")"
REUSE_FROM=$(python3 -c "import json;print(json.load(open('data/exp05/bill.json')).get('reused_shenglian_from') or '')")
REUSE=""
if [ -n "$REUSE_FROM" ]; then REUSE="--reuse-shenglian-from $REUSE_FROM"; fi
say "复用判定：${REUSE:-全重跑}"

say "T002 prescreen 开始…"
PYTHONPATH="$PYTHONPATH" "$QPY" scripts/exp05_prescreen.py $REUSE >> "$LOG" 2>&1
if [ $? -ne 0 ]; then say "ERROR prescreen 失败，退出"; exit 1; fi
say "prescreen 完成"

python3 -c "
import json
p = 'data/exp05/bill.json'
b = json.load(open(p))
b['confirmed'] = True
b['confirmed_by'] = '用户2026-10-04提前授权：校准稳定即自动测量'
b['confirmed_at'] = '$(date '+%Y-%m-%d %H:%M:%S')'
json.dump(b, open(p, 'w'), ensure_ascii=False, indent=2)
"
say "bill confirmed=true（授权记录已附）"

say "T003 submit 开始（烧机时）…"
PYTHONPATH="$PYTHONPATH" "$QPY" scripts/exp05_submit.py $REUSE >> "$LOG" 2>&1
code=$?
say "submit 退出码 $code"
exit $code

# Quickstart: Validate 01–04 (v2, Julia Round)

**Rule**: every scenario below runs on SAVED v2 data only — no ED/VQE rerun.
Re-running physics to "fix" a figure is forbidden (VII).

## Prerequisites

- Julia project env reproduced: `julia --project=. -e 'using Pkg; Pkg.instantiate()'`.
- Python pixi env retained ONLY for plotting/hash tooling.
- Completed datasets: `data/exp01/manifest.json`, `data/exp02/...`,
  `data/exp03/...`, `data/exp04/...` (schema `exp01-04/v2`).
- New Julia deps only through `Pkg.add`; new Python deps only through
  `CondaPkg.toml`. No venv/pip anywhere.

## Scenarios

### QS-1 — Rebuild 01 figures (SC-001)

```bash
export SOURCE_DATE_EPOCH=0
PY=.CondaPkg/.pixi/envs/default/bin/python
PYTHONPATH=. $PY -c "
import plotting.diagnostic.exp01 as d1, plotting.pra.exp01 as p1
d1.rebuild_all('data/exp01', 'figs/qs1diag')
p1.rebuild_all('data/exp01', 'figs/qs1pra')"
```

Expect: L=8 $\tilde Z_{\mathcal R}$ phase diagram, three $\delta=0$ raw gap
curves, $s=0.5$ scaling + free-intercept $(a,b)$ — hash-identical to committed
references (diagnostic + PRA pdf/png pairs).

### QS-2 — Rebuild 02 figures (SC-002)

```bash
export SOURCE_DATE_EPOCH=0
PY=.CondaPkg/.pixi/envs/default/bin/python
PYTHONPATH=. $PY -c "
import plotting.diagnostic.exp02 as d2, plotting.pra.exp02 as p2
d2.rebuild_all('data/exp02', 'figs/qs2diag')
p2.rebuild_all('data/exp02', 'figs/qs2pra')"
```

Expect: three-representative $S(q)$ comparison (distinguishable styles) +
four heatmaps; $Q$ regenerable from stored $S(\pi),O_{\rm str}$ alone.

### QS-3 — Verify 03/04 linkage (SC-003/SC-004/SC-005)

```bash
julia --project=. experiments_jl/exp04_verify.jl data/exp03 data/exp04
```

Expect: 98 exact; 490 selected each with 3-branch provenance;
all $E_{\rm var}\ge E_0-10^{-6}$; nesting holds; exit nonzero otherwise.

### QS-4 — Contract + cross-check tests

```bash
julia --project=. -e 'using Pkg; Pkg.test()'
```

Expect: grid identity, scan authority, Q-reconstruction, and
xcheck-baseline (5-pt + anchors + sampling) tests pass.

## Pipelines

- **Diagnostic**: extra info allowed, debugging/staging only.
- **PRA** (`pra-paper-figures`): pdf submission original + dpi=600 png preview
  under the same SHA256SUMS gate; `SOURCE_DATE_EPOCH=0` required for
  byte-identity.
- **Production gates** (plan Production Gates): QS-1 green → 02 production;
  QS-2 green → 03 production; QS-3 data + figures green → 04 production;
  QS-3/QS-4 + full verify green → converge. A red gate blocks downstream;
  gates never demand upstream recompute without a corruption diagnosis.

# Quickstart: Validate 01–04 From Saved Data

**Rule**: every scenario below runs on SAVED data only — no ED/VQE rerun
(SC-001/SC-002/SC-006). Re-running physics to "fix" a figure is forbidden (VII).

## Prerequisites

- Interpreter: `<repo>/.CondaPkg/.pixi/envs/default/bin/python`
  (numpy/scipy/qiskit-aer/matplotlib/pytest + editable qmeas, verified).
- Completed datasets: `data/exp01/manifest.json`, `data/exp02/...`,
  `data/exp03/...`, `data/exp04/...` (schema `exp01-04/v1`).
- Install nothing via pip; new deps only through `CondaPkg.toml`.

## Scenarios

### QS-1 — Rebuild 01 figures (SC-001)

```bash
PYTHON=<repo>/.CondaPkg/.pixi/envs/default/bin/python
$PYTHON -m plotting.diagnostic.exp01 --data data/exp01
$PYTHON -m plotting.pra.exp01 --data data/exp01 --out figs/pra/
```

Expect: L=8 $\tilde Z_{\mathcal R}$ phase diagram, four $\delta=1$ raw gap curves,
$s=0.5$ scaling scatter + free-intercept fit line with $(a,b)$ labels — all
identical (hash match) to committed reference figures.

### QS-2 — Rebuild 02 figures (SC-002)

```bash
$PYTHON -m plotting.diagnostic.exp02 --data data/exp02
$PYTHON -m plotting.pra.exp02 --data data/exp02 --out figs/pra/
```

Expect: three-representative $S(q)$ comparison + four heatmaps
($S(\pi),O_{\rm str},Q,\tilde Z_{\mathcal R}$); $Q$ panel regenerable from the
stored $S(\pi),O_{\rm str}$ alone (contract q-reconstruction).

### QS-3 — Verify 03/04 linkage (SC-003/SC-004/SC-005)

```bash
$PYTHON -m experiments.exp04_verify --ref data/exp03 --var data/exp04
```

Expect: 98 exact records; 490 selected each with 3-branch provenance;
all $E_{\rm var}\ge E_0-10^{-6}$; all `accepted(p) ≤ baseline(p-1)+τ`;
exit nonzero otherwise (ERROR gate).

### QS-4 — Contract tests (fast, no data needed beyond fixtures)

```bash
$PYTHON -m pytest tests/contract -q
```

Expect: grid identity, scan authority, and Q-reconstruction tests pass.

## Pipelines

- **Diagnostic** (`plotting/diagnostic`): extra info allowed, for debugging and
  staging checks.
- **PRA** (`plotting/pra`): constrained by `pra-paper-figures` + experiment
  specs; style changes MUST NOT require physics reruns.
- **Reference-hash mechanism** (binding for CHK020): SHA256 over each figure
  file bytes, recorded in `figs/pra/SHA256SUMS`; QS-1/QS-2 "hash match" means
  byte-identical match against that file, mismatch is an ERROR gate.
  PRA figures are dual-produced (pdf submission original + same-figure png
  preview at dpi=600) under the same hash gate.
  PRA PDFs embed a creation timestamp: all hash-gate rebuilds MUST export
  `SOURCE_DATE_EPOCH=0` first, otherwise byte-identity cannot hold.

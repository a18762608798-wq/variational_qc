# Subset Timing Gate (T050, VIII.6) — Julia round

**Date**: 2026-09-30 | **Status**: GO (conditional, see below)
**Subset**: s∈{0.1,0.5,0.9} × δ∈{0,1} × 3 branches × p=1,2 = 36 branch runs
+ 6 exact-ref points, production budgets (DE maxsteps=300/popsize=10,
COBYLA ≤2000 evals), 8 threads.

## Measured

| Stage | Runs | Wall | Output |
|-------|------|------|--------|
| exp03 ref (6 pts) | 6 ED L=8 | 127 s (incl. first-call compile) | 56 K |
| exp04 branches (36 runs → 12 selected) | 36 VQE | 342 s | 392 K |
| verify | — | — | 0 violations, 0 nesting violations |

Mean ≈ 76 worker-s per branch-run at 8 threads (includes Yao compile
amortization; steady-state faster).

## Extrapolation to full production (1470 branch-runs + grids)

- 04: 1470 × ~76 s / 8 threads ≈ 4 h wall.
- 01 grid 2401 + gaps 196 + 02 heatmaps 2401 + 03 ref 98 (L=8 ED): minutes
  each at 8 threads.
- Data volume projected < 100 MB. Checkpoint/idempotent resume verified
  (killed-and-resumed runs in round 1; same protocol here).

## Decision

**GO** — full production fits an overnight workstation session at 8 threads.
Single-threaded 04 alone (~30 h) is rejected; run parallel per R6.

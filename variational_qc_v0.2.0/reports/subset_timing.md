# Subset Timing Gate (T051, VIII.6)

**Date**: 2026-09-30 | **Status**: VOID — timings below measured under the old
qmeas-env interpreter (Python 3.14.6); superseded by repo-local env rerun.
**Rerun status**: RERUN COMPLETE under repo-local env (Python 3.12.14).
36/36 chains + 12/12 selected, 0 τ violations, 0 nesting violations.
Physics excellent (typical gaps 1e-5..1e-4; s=0.5 δ=3 improves 0.48 → 4e-3
from p=1 to p=2). Old 143.9s figure was measured with the buggy energy_fn
(flat landscape, instant DE convergence) and is VOID.

## Rerun measured (repo-local env, 8 workers, memory-contended box)

- Wall ≈ 62+ min for 36 chains (≈14 worker-min/chain mean, high variance:
  dim-4 δ=1 runs converge in ~1 min, dim-8 δ=3 runs hit full DE/COBYLA
  budgets; one p=2 warm chain took 728 s alone uncontended).
- Peak RSS ≈ 125 MB/process; box has 8 CPUs but only ~2 GB free RAM —
  8-way Aer workers thrash; 2–4 workers recommended.
- Output: 6 ref (32 K) + 36 branch + 12 selected (~200 K).

## Revised extrapolation to full production (1470 branch-runs)

- Serial: ~75–150 h. 4 workers (recommended): ~20–40 h. 8 workers on THIS
  box: NOT recommended (memory contention inflates per-eval cost 10x).
- Data volume projected < 50 MB. Checkpoint/idempotency verified by the
  interrupted-then-resumed rerun itself.

## Decision

**CONDITIONAL GO**: launch full production only with ≤4 workers as a
multi-day/background workload, OR revisit DE budgets (maxiter/popsize/tol —
method stays DE+COBYLA per doc, budgets are plan-level) after user sign-off.
Single-core and 8-way-on-this-box are both rejected by measurement.
**Subset** (plan Performance Goals): s∈{0.1,0.5,0.9} × δ∈{1,3} × 3 branches
× p=1,2 = 36 branch runs + 6 exact-ref points, production budgets
(DE maxiter=300/popsize=10, COBYLA ≤2000 evals).

## Measured (single core, workstation)

| Stage | Runs | Wall | Peak RSS | Output |
|-------|------|------|----------|--------|
| exp03 ref (6 pts) | 6 ED L=8 | 2.4 s | 125 MB | 32 K |
| exp04 branches (36 runs → 12 selected) | 36 VQE | 143.9 s | 125 MB | 200 K |
| verify | — | — | — | 0 violations, 0 nesting violations |

Mean ≈ 4 s per branch-run (τ gate + clamp verified green on real runs).

## Extrapolation to full production

| Scope | Estimate (1 core) | With 8 workers |
|-------|-------------------|----------------|
| 01 grid 2401 L=8 ED+obs | ~16 min | ~2 min |
| 01 gaps 196 (incl. L=16 sparse) | ~10–20 min | ~3 min |
| 02 heatmaps 2401 | ~16 min | ~2 min |
| 03 ref 98 | ~1 min | <1 min |
| 04 1470 branch runs | ~100 min | ~13 min |
| **Total** | **~2.5 h** | **~25 min** |

## Decision

**GO** — full production fits a workstation session even single-core, and
comfortably with the R5 process-pool parallelism (per-point checkpointing
already in place; reruns are idempotent). No checkpoint-frequency adjustment
needed at these data volumes (total output projected < 50 MB).

# Final Constitution Check I–XI + XI Absence Audit (T052)

**Date**: 2026-09-30 | **Scope**: code + tasks + specs for 001-ssh-xxz-experiments-01-04

| Article | Verdict | Evidence |
|---------|---------|----------|
| I physics source | PASS | No formula defined in code; all builders cite `doc/plan/theory/` |
| II one-way layers | PASS | `core` imports nothing from experiments/plotting; qmeas via thin adapter + 5-pt test |
| III reproducibility | PASS | Byte-exact seeds stored; NPZ+manifest provenance; atomic checkpoint; idempotent reruns (tested) |
| IV correctness first | PASS | 24 foundational unit tests green before production; dense-vs-sparse; τ + clamp enforced + tested |
| V controlled layers | PASS | 04 ideal only (Aer statevector, no shots/noise); fit/normalization in post-processing |
| VI data contracts | PASS | Explicit coords, failure states, source identity; contracts/ + contract tests green |
| VII figures from data | PASS | Both pipelines read saved data only; `pra-paper-figures` scoping in pra/ modules |
| VIII scalable methods | PASS | eigsh production; dense L≤8 only; subset gate GO (reports/subset_timing.md) |
| IX fail loudly | PASS | Failure records with reason; incompatible-overwrite refusal; per-point progress via counts |
| X workflow | PASS | Prior-stage decisions preserved (frozen grids, counts, optimizer settings) |
| XI scope lock | PASS | **Absence audit**: grep over src/experiments/plotting/tests/tools for finite-shot, shot-noise, hardware execution, physical-qubit, coupling_map, initial_layout, transpil*, mitigation, backend abstraction → zero hits. AerSimulator used with method='statevector' only. |

No violations. No Complexity Tracking entries.

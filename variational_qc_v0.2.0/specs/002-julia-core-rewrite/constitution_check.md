# Final Constitution Check I–XII + XI/XII Absence Audit (T053, 002 round)

**Date**: 2026-10-01 (re-audit; supersedes 2026-09-30) | **Scope**: Julia rewrite code + 002 specs + v2 data/figures

| Article | Verdict | Evidence |
|---------|---------|----------|
| I physics source | PASS | Formulas referenced from `doc/plan/theory/` (+XII H.md pin); no physics defined in code |
| II one-way layers | PASS | Julia core/experiment/script layers; QMeasPort minimal port + equivalence test |
| III reproducibility | PASS | Byte-exact seeds stored; v2 NPZ+manifest provenance; atomic checkpoint; idempotent resume (tested) |
| IV correctness first | PASS | Foundational tests gate production; dense-vs-sparse check; τ enforced; nesting clamp |
| V controlled layers | PASS | 04 ideal only; raw preserved; fit in post-processing |
| VI data contracts | PASS | Explicit coordinates, failure states, source/backend identity; contracts/ directory |
| VII figures from data | PASS | Pipelines read saved v2 data only; `pra-paper-figures` scoping |
| VIII scalable methods | PASS | KrylovKit production ED; dense L≤8 only; direct-assembly builder with kron regression (IV.7); subset timing gate |
| IX fail loudly | PASS | Failure records with reason; incompatible-overwrite refusal; per-point progress |
| X workflow | PASS | Binding Clarifications (D-001–D-003) preserved into plan/tasks |
| XI scope lock | PASS | Absence audit 2026-10-01: zero implementation hits in code; ban statements only in spec/plan/task prose |
| XII Julia stack | PASS w/ record | Archived Python core: zero modifications (git diff clean under `src/`); one ADDITION `src/SSHXXZ.jl` (3-line Pkg.test entry shim, no physics, T054-gate-driven); schema v2; v1 void-with-anchors; tolerance D-002 amended (see below) |

Absence-audit method (2026-10-01): grep over `src_jl experiments_jl test
plotting tools specs/002-julia-core-rewrite`
for finite-shot, shot-noise, hardware execution, physical-qubit, coupling_map,
initial_layout, transpil*, mitigation, backend abstraction, 05/hardware VQE —
zero implementation hits (ban/out-of-scope statements in spec prose only).

D-002 operational change record (2026-10-01): original D-002 tolerance item
"v2 records vs archived v1 baseline, energies <1e-8" removed from
`contracts/xcheck-baseline.md` as unachievable — $H$ redefined v1 linear-$\delta$
to v2 exp-$\delta$ ($O(1)$ spectral gap, single-point verified 3.6).
Substituted same-$H$ trio (builder equivalence <1e-10, anchors exact, new-$H$
Heisenberg limits <1e-8); verified in `xcheck_report.md` (T052 PASS).
`grid-01-02.md` §5 subset re-mapped to isomorphic on-grid points.

No violations. No Complexity Tracking entries.

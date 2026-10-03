# Implementation Plan: Julia Core Rewrite (SSH-XXZ 01–04)

**Branch**: `002-julia-core-rewrite` | **Date**: 2026-09-30 |
**Spec**: [spec.md](spec.md) | **Constitution**: v0.3.0

**Input**: Feature specification from `specs/002-julia-core-rewrite/spec.md`
plus frozen clarify decisions D-001–D-003.

**Authority ranking**: spec.md Binding Clarifications (frozen 2026-09-30) >
`doc/plan/experiment/{01,02,03,04_ideal_vqe}.md` +
`doc/plan/theory/{H,psi0,ansatz,cost_fun,topological_op}.md` > `theory/`.
New $H$ (exponential anisotropy, δ=0 isotropic point, scan lines δ=0,0.85).
`src/ssh_xxz` Python core is archived READ-ONLY; 05/hardware untouched.

**Execution rule (user)**: test runs and production runs execute continuously —
no voluntary breakpoints; user interrupts on problems. Data checkpoints stay.

## Summary

Rewrite the 01–04 compute core in Julia (KrylovKit sparse ED, Yao.jl ideal
statevector, BlackBoxOptim DE + NLopt COBYLA chain mirroring round 1),
recompute everything under the new Hamiltonian into schema `exp01-04/v2`
(same NPZ+manifest layout, new schema string), cross-check against the
archived Python baseline (E<1e-8/obs<1e-6), and keep diagnostic + PRA figure
pipelines working from v2 data. All Phase 0 unknowns resolved in
[research.md](research.md); zero NEEDS CLARIFICATION remain.

## Technical Context

**Language/Version**: Julia 1.12, repo-root project env (`Project.toml` +
`Manifest.toml`, Pkg-managed). Python env retained ONLY for plotting/hash
tooling; no Python compute beyond the frozen baseline.

**Primary Dependencies**: KrylovKit.jl (sparse ED), Yao.jl (ideal statevector),
BlackBoxOptim.jl (DE global step), NLopt.jl (COBYLA polish), NPZ.jl + JSON3.jl
(v2 persistence), Test.jl (stdlib testing). New deps only via `Pkg.add`.

**Storage**: per-point `.npz` (NPZ.jl) + JSON manifest, schema `exp01-04/v2`
(see [data-model.md](data-model.md)); atomic tmp+rename checkpoint per point.
Format deliberately identical to v1 so figure/hash tooling is unchanged.

**Testing**: Julia Test stdlib — `test/unit` (IV.2 primitives), `test/contract`
(grid/scan/Q/cross-check contracts), `test/integration` (resume idempotency,
SC rebuild); entry `test/runtests.jl`.

**Target Platform**: Linux workstation.

**Project Type**: numerical experiment suite, single project (Julia package
dirs alongside the archived Python tree).

**Performance Goals**: full cycle unattended with per-point checkpointing;
04 branch runs dominate — production gated on representative-subset timing
(VIII.6), same as round 1.

**Constraints**: sparse production ED only (KrylovKit eigsolve tol 1e-10);
dense `eigen` for L≤8 cross-validation only; $\theta\in[-\pi,\pi]$;
$\tau=10^{-6}$ violation threshold; δ=0 halved params ($\theta_1=\theta_2$,
no extra deletion); δ=0.85 full params; AFM-branch first-layer first
even-sublayer two ZZ frozen 0 independent of scan δ, no expanded freezing
from layer 2; idempotent resume, incompatible-config overwrite refused;
Python core files MUST NOT be modified.

**Scale/Scope**: 2401 grid + 147 gap (L=8,12,16) + 2401 heatmaps + 3 S(q) +
98 exact-ref + 1470 branch runs (490 selected); strictly 01–04 ideal.
(26 out-of-scope L=20 gap records deleted per 2026-09-30 authorization.)

## Constitution Check (pre-design)

*GATE: passed before Phase 0 research. Re-checked after Phase 1 design below.*

- **I**: PASS — formulas referenced from `doc/plan/theory/` (+XII H.md pin); no physics defined here.
- **II**: PASS — Julia core/experiment/plotting one-way layers; qmeas-equivalent is a minimal port (D-003), not a rewrite.
- **III**: PASS — explicit seeds stored, v2 provenance, checkpoint/resume, idempotent reruns (v2 schema; v1 void per XII exception).
- **IV**: PASS — small-system tests gate production; dense-vs-sparse check; τ enforced; nesting clamp.
- **V**: PASS — 04 ideal only; raw preserved; fit in post-processing.
- **VI**: PASS — explicit coordinates, failure states, source/backend identity (`julia-krylovkit`, `julia-yao`); contracts/ directory.
- **VII**: PASS — pipelines read saved v2 data only; `pra-paper-figures` constrains output.
- **VIII**: PASS — sparse production ED; subset timing before full launch.
- **IX**: PASS — explicit failures, no silent fallback, per-point progress.
- **X**: PASS — prior-stage (Binding Clarifications) decisions preserved.
- **XI**: PASS — no finite-shot/hardware/05 content in any artifact.
- **XII**: PASS — Julia stack lock respected; Python core untouched; schema v2; v1 void-with-anchors; qmeas paused in favor of baseline cross-check; tolerance frozen (D-002).

Gates: no violations → no Complexity Tracking entries. (ERROR would fire otherwise.)

## Project Structure

### Documentation (this feature)

```text
specs/002-julia-core-rewrite/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── grid-01-02.md
│   ├── scan-03-04.md
│   ├── q-reconstruction.md
│   └── xcheck-baseline.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src_jl/SSHXXZ/               # Julia package (new; Python src/ssh_xxz archived read-only)
├── Core/                    # H builder, symmetries, observables, initial states,
│                            # ansatz circuit, physical cost (no I/O/plot deps)
├── ED/                      # KrylovKit production ED + dense small-L reference
├── VQE/                     # ideal optimizer: DE+COBYLA, warm start, clamp
├── QMeasPort/               # minimal H/initial-state port + equivalence test
└── IO/                      # schema-versioned NPZ persistence, manifest,
                             # checkpoint/resume, provenance
experiments_jl/
├── exp01_phase.jl            # orchestration only
├── exp02_observables.jl
├── exp03_reference.jl
├── exp04_ideal.jl
└── run_all.jl                # point-level parallel launcher
test/                        # Julia Test stdlib layout (runtests.jl entry)
├── unit/
├── contract/
└── integration/
plotting/                    # Python figure pipelines, v2 ACTIVE (matplotlib):
├── diagnostic/              # debug/staging figures, saved data only
├── pra/                     # publication figures (pra-paper-figures), saved data only
├── v2read.py                # v2 record reader (npz + sidecar JSON), shared by all plots
└── pra_style.py             # PRA single-column style helper (vendored skill script)
data/                        # v2 datasets (per-exp dirs + shared/ + manifests)
figs/                        # figure outputs only (diagnostic + pra pairs + SHA256SUMS)
```

**Structure Decision**: single project, Julia package dirs beside the archived
Python tree. One-way layering per II; `experiments_jl/*` never reimplements
physics; plotting reads saved v2 data only. No backend abstraction layer (XI/XII).

## Complexity Tracking

> No Constitution Check violations → this section intentionally empty.

## Production Gates (per-experiment figure gates, doc 00/01/03/04)

No experiment's production starts until the previous story's checkpoint is
green (rebuild + hash gate). Edges:

- **G01**: US1 data complete → `rebuild_01` diagnostic + PRA pairs regenerate
  hash-identically → 02 production may start.
- **G02**: US2 data complete → `rebuild_02` pairs green → 03 production may start.
- **G03**: US3 data complete → `rebuild_03` pairs green → 04 production may start.
- **G04**: US4 data complete → `verify_04` zero-violation + comparison pairs
  green → converge.

A red gate blocks its downstream edge; it never re-triggers upstream recompute
unless the gate diagnosis proves upstream data corrupt.

## Phase 0 → Phase 1 traceability

- D-001 stack → `src_jl` layout, `test/` primitives, optimizer module.
- D-002 tolerance/coverage → `contracts/xcheck-baseline.md`, τ tests.
- D-003 minimal port → `QMeasPort/` + 5-point equivalence test.
- Storage/provenance → `data-model.md`, manifest schema v2.
- Parallelism/resume → `run_all.jl`, idempotency tests.

## Constitution Check (post-design)

Re-evaluated after Phase 1 artifacts ([data-model.md](data-model.md),
[contracts/](contracts/), [quickstart.md](quickstart.md)): all gates I–XII
remain PASS. No artifact modifies the Python core (XII); v1 data untouched by
design artifacts (voiding is a runtime step gated by converge archive);
no hardware/finite-shot concepts (XI). No new violations → Complexity
Tracking stays empty.

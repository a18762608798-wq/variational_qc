# Implementation Plan: SSH-XXZ Experiments 01–04

**Branch**: `001-ssh-xxz-experiments-01-04` | **Date**: 2026-09-30 |
**Spec**: [spec.md](spec.md) | **Constitution**: v0.2.0

**Input**: Feature specification from `specs/001-ssh-xxz-experiments-01-04/spec.md`
plus user planning directives (authority ranking, Phase 0 items R1–R5, Phase 1
artifacts, double Constitution Check, XI gate).

**Authority ranking**: spec.md Binding Clarifications (frozen 2026-09-30) >
`doc/plan/experiment/{01,02,03,04_ideal_vqe}.md` +
`doc/plan/theory/{H,psi0,ansatz,cost_fun,topological_op}.md` > `theory/`.
Conflicts resolve toward `doc/`; physics is never redefined here; 05/hardware
is untouched.

## Summary

Implement experiments 01–04 of the SSH-XXZ cycle: L=8 exact phase structure on
the frozen 49×49 interior grid (01), observable characterization with frozen
representatives (02), L=8 exact reference on two scan lines (03), and ideal
noiseless variational preparation p=1..5 over three initial-state branches (04).
Reusable core (Hamiltonian/observables/ansatz/ED/optimizer), orchestration
scripts, versioned per-point persistence with checkpoint/resume, and decoupled
diagnostic + PRA plotting pipelines. All Phase 0 unknowns resolved in
[research.md](research.md); zero NEEDS CLARIFICATION remain.

## Technical Context

**Language/Version**: Python 3.12.14 via the repo-local julia-condapkg env
(`.CondaPkg/.pixi/envs/default/bin/python`, built from `Project.toml` +
`CondaPkg.toml`; qmeas reused editable).
No venv, no system pip (per `env-python` skill).

**Primary Dependencies**: numpy 2.5.1, scipy 1.18.0, qiskit 2.5.1 + qiskit-aer
(04 ideal statevector), matplotlib 3.11.2, pytest 9.1.1; stdlib json/hashlib for
provenance. New deps only via `CondaPkg.toml`.

**Storage**: per-point `.npz` + JSON manifest, schema `exp01-04/v1`
(see [data-model.md](data-model.md)); atomic tmp+rename checkpoint per point.

**Testing**: pytest — `tests/unit` (IV.2 primitives), `tests/contract`
(grid/scan/Q contracts), `tests/integration` (resume idempotency, SC rebuild).

**Target Platform**: Linux workstation.

**Project Type**: numerical experiment suite (reusable core lib + orchestration
scripts + plotting pipelines), single project.

**Performance Goals**: full cycle completes unattended with per-point
checkpointing; dominant cost is the 1470 branch optimizations — production
launch gated on representative-subset timing (VIII.6, binding for CHK030):
subset = $s\in\{0.1,0.5,0.9\}\times\delta\in\{1,3\}\times3$ branches
$\times p=1,2$ (36 runs) + the 5-point ED equivalence subset; record
runtime/memory/output-size estimates in run metadata and extrapolate to the
full 1470 + 2401 ED scope — go only when the extrapolation fits the
workstation budget, otherwise adjust parallelism/checkpoint frequency first.

**Constraints**: sparse production ED only (`eigsh k=2 SA tol=1e-10`); dense
`eigh` for L≤8 cross-validation only; $\theta\in[-\pi,\pi]$; $\tau=10^{-6}$
variational-violation threshold; idempotent resume, incompatible-config
overwrite refused.

**Scale/Scope**: 2401 grid points + 196 gap points + 98 exact-ref + 1470 branch
runs (490 selected); strictly 01–04, no 05/hardware.

## Constitution Check (pre-design)

*GATE: passed before Phase 0 research. Re-checked after Phase 1 design below.*

- **I (physics source of truth)**: PASS — all formulas referenced from
  `doc/plan/theory/` + spec Binding Clarifications; plan defines no physics.
- **II (modular one-way)**: PASS — core/experiment/plotting layers, core free of
  plotting/experiment imports; qmeas via thin adapter + equivalence test.
- **III (reproducibility)**: PASS — explicit seeds stored, per-point NPZ +
  manifest provenance, checkpoint/resume, idempotent reruns.
- **IV (correctness first)**: PASS — small-system tests gate production;
  dense-vs-sparse cross-check; $E_{\rm var}\ge E_0-\tau$ enforced; nesting
  clamp by construction + test.
- **V (controlled layers)**: PASS — 04 is ideal only (no shots/noise/mapping);
  raw data preserved, fit/normalization in post-processing.
- **VI (data contracts)**: PASS — explicit coordinates, failure states,
  source/backend identity; contracts/ directory.
- **VII (figures from saved data)**: PASS — diagnostic vs PRA pipelines read
  saved data only; `pra-paper-figures` constrains publication output.
- **VIII (scalable methods)**: PASS — sparse production ED; dense restricted;
  subset timing before full launch.
- **IX (fail loudly)**: PASS — explicit failure records, no silent fallback,
  per-point progress, warnings in metadata.
- **X (SpecKit workflow)**: PASS — this plan preserves prior-stage decisions.
- **XI (01–04 scope lock)**: PASS — no finite-shot/Hardware/coupling_map/
  layout/transpilation/mitigation/generic-backend abstraction anywhere in plan,
  research, data model, contracts, or quickstart.

Gates: no violations → no Complexity Tracking entries. (ERROR would have fired
on any gate failure.)

## Project Structure

### Documentation (this feature)

```text
specs/001-ssh-xxz-experiments-01-04/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── grid-01-02.md
│   ├── scan-03-04.md
│   └── q-reconstruction.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/ssh_xxz/
├── core/                 # H builder, symmetries, observables, initial states,
│                         # ansatz circuit, physical cost (reusable, no I/O/plot deps)
├── ed/                   # sparse production ED + dense small-L reference
├── vqe/                  # ideal optimizer: DE+COBYLA, warm start, clamp
├── adapters/
│   └── qmeas_adapter.py  # thin adapter onto qmeas + equivalence test
└── io/                   # schema-versioned NPZ persistence, manifest,
                          # checkpoint/resume, provenance
experiments/
├── exp01_phase.py        # orchestration only (read config → call core → save → plot trigger)
├── exp02_observables.py
├── exp03_reference.py
└── exp04_ideal.py
plotting/
├── diagnostic/           # debug/staging figures (data only)
└── pra/                  # publication figures (pra-paper-figures constrains)
tests/
├── unit/
├── contract/
└── integration/
```

**Structure Decision**: single-project layout (user directive). One-way layering
per II: `core` ← `experiments`/`plotting` depend inward only; `experiments`
never reimplements physics; `plotting` never runs physics. No backend
abstraction layer (XI).

## Complexity Tracking

> No Constitution Check violations → this section intentionally empty.

## Phase 0 → Phase 1 traceability

- R1 gap s-resolution → `contracts/scan-03-04.md` (coordinate authority),
  `data-model.md` FiniteSizeGapPoint.
- R2 q-grid → `contracts/q-reconstruction.md`, `data-model.md` S(q) fields.
- R3 tolerance + clamp → `data-model.md` failure enum + provenance flags,
  `contracts/scan-03-04.md` selection rule.
- R4 solver/qmeas/optimizer/fit → `tests/` layout, adapter module, post-design
  check below.
- R5 Technical Context → Source Code tree above, `quickstart.md` commands.

## Constitution Check (post-design)

Re-evaluated after Phase 1 artifacts ([data-model.md](data-model.md),
[contracts/](contracts/), [quickstart.md](quickstart.md)): all gates I–XI remain
PASS. In particular: no artifact introduces hardware/finite-shot concepts (XI);
no artifact redefines physics (I, FR-001); Q stays derived-only (FR-004,
AS-02.3); coordinates stay explicit (FR-009); failures stay explicit (FR-008).
No new violations → Complexity Tracking stays empty.

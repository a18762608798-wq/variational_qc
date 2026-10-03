# Tasks: SSH-XXZ Experiments 01–04

**Input**: Design documents from `specs/001-ssh-xxz-experiments-01-04/`
(spec.md, plan.md, research.md R1–R5, data-model.md, contracts/, quickstart.md)

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/,
constitution v0.2.0

**Tests**: MANDATORY this cycle (Constitution IV + FR-001–FR-010) — TDD:
test tasks are listed FIRST in each phase and MUST FAIL before implementation.

**Organization**: grouped by user story for independent implementation/testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no pending dependencies)
- **[Story]**: [US1]–[US4] for story phases only
- Every task carries its exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: interpreter, dependency rule, directory tree, test harness

- [X] T001 Create directory tree + package `__init__` files per plan.md Source Code layout (`src/ssh_xxz/{core,ed,vqe,adapters,io}`, `experiments`, `plotting/{diagnostic,pra}`, `tests/{unit,contract,integration}`, `data`)
- [X] T002 [P] Record repo-local pixi interpreter (`.CondaPkg/.pixi/envs/default/bin/python`) + CondaPkg-only rule (no venv/pip) in `env/INTERPRETER.md` and verify imports (`numpy,scipy,qiskit,qiskit_aer,matplotlib,pytest,qmeas`)
- [X] T003 [P] Create pytest configuration in `pyproject.toml` (`testpaths=tests`)
- [X] T004 [P] Create shared fixtures (frozen grid arrays, temp data dir) in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: reusable physics/numerics + persistence that every story needs

**⚠️ CRITICAL**: No user story work begins until this phase is complete.
Test tasks T005–T011, T019 MUST be written FIRST and FAIL before T012–T022.

### Tests (write first, FAIL first)

- [X] T005 [P] Unit test Hamiltonian bond placement + OBC behavior in `tests/unit/test_hamiltonian.py` (IV.2)
- [X] T006 [P] Unit test initial-state preparation + P=−2 sector membership in `tests/unit/test_initial_states.py` (IV.2)
- [X] T007 [P] Unit test ansatz parameter count/order (`Nθ=Lp`, `Lp/2` at δ=1, F-rule, fixed layer order) in `tests/unit/test_ansatz.py` (IV.2)
- [X] T008 [P] Unit test observable evaluation conventions in `tests/unit/test_observables.py` (IV.2)
- [X] T009 [P] Unit test physical cost + min-over-branches/restarts selection in `tests/unit/test_cost.py`
- [X] T010 [P] Unit test byte-exact seed-derivation vectors in `tests/unit/test_seeds.py`
- [X] T011 [P] Unit test NPZ manifest schema + atomic write + hash idempotency + raw immutability in `tests/unit/test_io.py` (III.6–7; FR-006/V.5: raw bitwise unchanged after post-processing/fit/plotting, no 0–1 overwrite of raw)
- [X] T012 [P] 5-point 1e-10 qmeas-vs-native equivalence test in `tests/unit/test_qmeas_equivalence.py` (II.5)

### Implementation (blocking)

- [X] T013 [P] Implement H builder + symmetries in `src/ssh_xxz/core/hamiltonian.py` (`doc/plan/theory/H.md`; sparse + dense paths, no physics redefinition)
- [X] T014 [P] Implement triv/topo/AFM initial states in `src/ssh_xxz/core/initial_states.py` (`doc/plan/theory/psi0.md`)
- [X] T015 [P] Implement S(q)/S(π)/Ostr/Q-derived-only/Z̃R in `src/ssh_xxz/core/observables.py` (`doc/plan/theory/topological_op.md`)
- [X] T016 [P] Implement orbit ansatz circuit in `src/ssh_xxz/core/ansatz.py` (`doc/plan/theory/ansatz.md`; halving + GHZ-freeze hooks)
- [X] T017 [P] Implement physical cost + branch selection in `src/ssh_xxz/core/cost.py` (`doc/plan/theory/cost_fun.md`)
- [X] T018 [P] Implement sparse production ED (`eigsh k=2 SA tol=1e-10`) + dense L≤8 reference in `src/ssh_xxz/ed/solver.py` (VIII; dense for cross-validation only)
- [X] T019 Implement qmeas thin adapter in `src/ssh_xxz/adapters/qmeas_adapter.py` (II.5; native fallback documented, no second physics)
- [X] T020 [P] Implement NPZ+manifest store + checkpoint/resume in `src/ssh_xxz/io/store.py` (schema `exp01-04/v1`; explicit coordinates FR-009; failure states FR-008)
- [X] T021 [P] Implement byte-exact seed derivation (`SHA256→uint32`) in `src/ssh_xxz/vqe/seeds.py`
- [X] T022 Implement ideal optimizer (DE+COBYLA, n_seeds=3, warm start U(−0.3,0.3), n_restarts=3, clamp, θ box) in `src/ssh_xxz/vqe/optimizer.py` (`doc/plan/experiment/04_ideal_vqe.md`)

**Checkpoint**: foundation ready — stories may now proceed (sequentially P1→P4 or in parallel if staffed)

---

## Phase 3: User Story 1 — Exact Phase Structure (Priority: P1) 🎯 MVP

**Goal**: L=8 Z̃R phase diagram on frozen 49×49 grid + 4-size raw gap + scaling fit

**Independent Test**: SC-001 — rebuild phase diagram, four gap curves, s=0.5 scaling figure from saved data only

### Tests (write first, FAIL first)

- [X] T023 [P] [US1] Contract test 01/02 grid identity in `tests/contract/test_grid_01_02.py` (`contracts/grid-01-02.md` rules 1–5)
- [X] T024 [P] [US1] Integration test SC-001 rebuild-from-data in `tests/integration/test_sc001_rebuild.py`
- [X] T025 [P] [US1] Unit test free-intercept polyfit post-processing in `tests/unit/test_fit.py` (CL-002; fit never feeds physics, V.5)

### Implementation

- [X] T026 [P] [US1] Implement 2401-point Z̃R grid runner in `experiments/exp01_phase.py` (reads canonical grid; PhaseGridPoint with "(L,s,δ)" + observables + provenance `"source=exact"`)
- [X] T027 [US1] Implement 196-point gap runner (4 L × 49 reused s_i) in `experiments/exp01_phase.py` (R1; FiniteSizeGapPoint with "(L,s,δ=1,E0,E1,Δraw)"; raw full-Hilbert-space, no P penalty, s→1 collapse preserved)
- [X] T028 [P] [US1] Implement scaling post-proc (polyfit Δ=a/L+b, report a,b) in `plotting/diagnostic/exp01_scaling.py` (CL-002, plotting/post-processing only)
- [X] T029 [P] [US1] Implement diagnostic figures (data-only) in `plotting/diagnostic/exp01.py`
- [X] T030 [P] [US1] Implement PRA figures (data-only, `pra-paper-figures`) in `plotting/pra/exp01.py`

**Checkpoint**: US1 fully functional and independently testable (MVP)

---

## Phase 4: User Story 2 — Observable Characterization (Priority: P2)

**Goal**: heatmaps + 3-representative S(q) with frozen q-grid; Q derived-only

**Independent Test**: SC-002 — rebuild S(q) comparison + four heatmaps from saved data only

### Tests (write first, FAIL first)

- [X] T031 [P] [US2] Contract test Q reconstruction-only in `tests/contract/test_q_reconstruction.py` (`contracts/q-reconstruction.md` rules 1–5)
- [X] T032 [P] [US2] Integration test SC-002 rebuild in `tests/integration/test_sc002_rebuild.py`

### Implementation

- [X] T033 [P] [US2] Implement heatmap runner (S(π), Ostr, Q-derived, Z̃R-referenced) in `experiments/exp02_observables.py` (shares canonical grid + state convention with 01)
- [X] T034 [US2] Implement 3-representative S(q) curves with identical 49-point q array (linspace 0..2π, π explicit) saved per record in `experiments/exp02_observables.py` (R2 amended; implements contract §5 q-grid; frozen (0.02,0.06)/(0.98,0.06)/(0.5,2.94); distinct markers/linestyles so overlapping lines stay visible)
- [X] T035 [P] [US2] Implement diagnostic figures (data-only) in `plotting/diagnostic/exp02.py`
- [X] T036 [P] [US2] Implement PRA figures (data-only) in `plotting/pra/exp02.py`

**Checkpoint**: US1 + US2 independently functional

---

## Phase 5: User Story 3 — L=8 Exact Reference (Priority: P3)

**Goal**: 98 exact records on two scan lines as 04's sole ground truth

**Independent Test**: SC-003 — 98 coordinates present (record or explicit failure); s-array loadable as authority

### Tests (write first, FAIL first)

- [X] T037 [P] [US3] Contract test 03→04 s authority in `tests/contract/test_scan_authority.py` (AS-03.3; `contracts/scan-03-04.md` rule 1)
- [X] T038 [P] [US3] Integration test SC-003 count in `tests/integration/test_sc003_counts.py`

### Implementation

- [X] T039 [US3] Implement 98-point exact-ref runner in `experiments/exp03_reference.py` (ExactReferencePoint with "(L=8,s,δ,E0,S_exact(π),O_str,exact)"; `source=exact`)
- [X] T040 [P] [US3] Implement diagnostic reference curves (data-only) in `plotting/diagnostic/exp03.py`
- [X] T041 [P] [US3] Implement PRA reference curves (data-only) in `plotting/pra/exp03.py`

**Checkpoint**: all stories so far independently functional

---

## Phase 6: User Story 4 — Ideal Variational Preparation (Priority: P4)

**Goal**: 490 selected + 1470 branch results with frozen optimizer, τ gate, nesting clamp

**Independent Test**: SC-004/SC-005 — counts + 3-branch provenance + Evar≥E0−τ throughout

### Tests (write first, FAIL first)

- [X] T042 [P] [US4] Unit test τ violation flag (Evar<E0−τ → failed record) in `tests/unit/test_variational_principle.py` (AS-04.4)
- [X] T043 [P] [US4] Unit test nesting clamp (accepted≤baseline+τ, `from_baseline` flag) in `tests/unit/test_nesting_clamp.py` (AS-04.5)
- [X] T044 [P] [US4] Integration test SC-004/005 in `tests/integration/test_sc004_005.py`
- [X] T044b [US4] Implement QS-3 verifier in `experiments/exp04_verify.py` (reads data/exp03+exp04 manifests; asserts 98 exact / 490 selected / 3-branch provenance / Evar≥E0−τ / nesting+from_baseline; nonzero exit on failure; serves quickstart.md QS-3 run by T049)

### Implementation

- [X] T045 [US4] Implement 1470 branch-run orchestrator in `experiments/exp04_ideal.py` (loads 03 s authority; θ box; δ=1 halved; δ=3 AFM ZZ frozen 0; byte-exact seeds; n_seeds=3/n_restarts=3; clamp; VariationalBranchResult with "(s,δ,p,initial-state branch)" + θ* + E_branch + `from_baseline∈{0,1}`)
- [X] T046 [US4] Implement argmin selection + exact-record join (orphan rejection) in `experiments/exp04_ideal.py` (AS-04.2; SelectedVariationalResult links exact coordinates; depends on T045)
- [X] T047 [P] [US4] Implement diagnostic comparison figures (data-only) in `plotting/diagnostic/exp04.py`
- [X] T048 [P] [US4] Implement PRA comparison figures (data-only) in `plotting/pra/exp04.py`

**Checkpoint**: all four stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: validation gates, hashes, timing gate, final compliance

- [ ] T049 [P] Execute QS-1–QS-4 validation runs per `specs/001-ssh-xxz-experiments-01-04/quickstart.md` and record outcomes
- [X] T050 [P] Implement SHA256SUMS hash gate for datasets + reference figures in `tools/hash_gate.py` (SC-006 identity)
- [X] T051 Execute 36-run representative-subset timing gate in `reports/subset_timing.md` (VIII.6; gates full launch; subset = s∈{0.1,0.5,0.9}×δ∈{1,3}×3 branches×p=1,2 per plan Performance Goals + 5-point ED subset; record runtime/memory/output-size + extrapolation + go/no-go)
- [X] T052 Final Constitution Check I–XI + XI absence audit (no finite-shot/hardware/coupling_map/layout/transpilation/mitigation/backend abstraction) recorded in `specs/001-ssh-xxz-experiments-01-04/constitution_check.md`
- [ ] T053 Run full pytest suite green (`tests/`) and re-run end-to-end validation per `specs/001-ssh-xxz-experiments-01-04/quickstart.md` (QS-1–QS-4)
- [X] T055 PRA PNG dual output on disk (each `plotting/pra/exp0*.py` figure saved as pdf + dpi=600 png; pdf stays submission original, png same-source preview; diagnostic/ untouched)
- [X] T054 Implement point-level parallel launcher in `experiments/run_all.py` (ProcessPoolExecutor over points/chains; idempotent resume; deterministic seeds give bit-identical results vs serial; R5)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — starts immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all stories
- **Stories (Phases 3–6)**: depend on Foundational; then P1→P2→P3→P4 (or parallel if staffed; US3 authority feeds US4 data at runtime, code-independent)
- **Polish (Phase 7)**: depends on all stories complete

### User Story Dependencies

- **US1 (P1)**: after Foundational; no story dependencies — MVP
- **US2 (P2)**: after Foundational; reads US1 canonical grid/Z̃R at runtime, independently testable via fixtures
- **US3 (P3)**: after Foundational; independent
- **US4 (P4)**: after Foundational; consumes US3 s-array + exact records at runtime (contract-tested)

### Within Each Story

Tests MUST be written and FAIL before implementation → core physics before orchestration → orchestration before plotting → checkpoint per story.

### Parallel Opportunities

- [P] Setup tasks (T002–T004), [P] Foundational tests + implementations (distinct files), per-story [P] tests and plotting files, stories 1–4 in parallel post-foundation if staffed.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together (FAIL first):
Task: "Contract test 01/02 grid identity in tests/contract/test_grid_01_02.py"      # T023
Task: "Integration test SC-001 rebuild in tests/integration/test_sc001_rebuild.py" # T024
Task: "Unit test free-intercept polyfit in tests/unit/test_fit.py"                 # T025
# Then US1 implementations with distinct files in parallel:
Task: "2401-point Z̃R grid runner in experiments/exp01_phase.py"                   # T026
Task: "Scaling post-proc in plotting/diagnostic/exp01_scaling.py"                 # T028
Task: "Diagnostic figures in plotting/diagnostic/exp01.py"                        # T029
Task: "PRA figures in plotting/pra/exp01.py"                                      # T030
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → 2. Phase 2 Foundational → 3. Phase 3 US1 → **STOP and VALIDATE** SC-001 → demo if ready

### Incremental Delivery

Setup + Foundational → US1 (MVP) → US2 → US3 → US4 → Polish; each increment independently testable, no breakage of prior stories.

### Parallel Team Strategy

Together: Setup + Foundational. Then Developer A: US1, B: US2, C: US3, D: US4 (US4 runtime data depends on US3 outputs via contract, code work parallelizable with fixtures).

---

## Notes

- [P] = different files, no pending dependencies; [USx] maps task to story
- data-model constraints quoted verbatim in task text (no implementation-time discretion)
- Commit after each task or logical group; stop at any checkpoint to validate
- Forbidden: vague tasks, same-file parallel conflicts, cross-story code dependencies, any 05/hardware/shots/backend-abstraction work (XI)

---

## Phase 8: Convergence (archive assessment 2026-09-30, deferred to Julia round)

**Archive record (verified on disk, read-only)**:
- 01 COMPLETE: grid 2401/2401 ok + gaps 196/196 ok; QS-1 diag 3 + PRA 3 pairs, hashes green.
- 02 COMPLETE: heat 2401/2401 ok + sq 3/3 ok (49-pt grid); QS-2 diag 5 + PRA 5 pairs, hashes green.
- 03 COMPLETE: 98/98 ok; ref-curve figures + hashes green.
- 04 PARTIAL/DEFERRED: branch 331/1470 ok, selected 0/490; background terminated by reviewer; records idempotent-resumable; full production moves to the Julia round (model changes).
- Subset (method validation): 6 ref + 36 branch + 12 selected, 0 violations — stays as reference.
- Constitution: no violations in force; T052 audit predates post-audit bugfixes (see T060).

**Reviewer: hand-mark the items below deferred; do NOT execute in this round.**

- [ ] T056 Complete 04 production to 1470 branch + 490 selected and verify counts per SC-004 (partial)
- [ ] T057 Run τ + nesting verification on the full 04 set per SC-005 (partial)
- [ ] T058 Execute QS-3 03/04-linkage validation on full data per quickstart.md QS-3 (partial)
- [ ] T059 Close T049/T053 end-to-end validation per quickstart.md QS-1–QS-4 (partial)
- [ ] T060 Re-run final Constitution Check I–XI audit (T052 artifact predates Z̃R/resume/energy_fn fixes) per Constitution X (partial)
- [ ] T061 Render 04 comparison figures (diagnostic + PRA pairs) and hash-gate them per SC-006 (partial)

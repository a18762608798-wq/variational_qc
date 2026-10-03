# Tasks: Julia Core Rewrite (SSH-XXZ 01–04)

**Input**: Design documents from `specs/002-julia-core-rewrite/`
(spec.md, plan.md, research.md R1–R6, data-model.md, contracts/, quickstart.md)

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/,
constitution v0.3.0

**Tests**: MANDATORY this cycle (Constitution IV + FRs) — TDD: test tasks are
listed FIRST in each phase and MUST FAIL before implementation.

**Execution rule (user)**: test runs and production runs execute continuously —
no voluntary breakpoints; user interrupts on problems. Data checkpoints stay
(idempotent resume everywhere).

**Organization**: grouped by user story for independent implementation/testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependencies)
- **[Story]**: [US1]–[US4] for story phases only
- Every task carries its exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Julia project env, directory tree, test harness

- [X] T001 Create directory tree + module stubs per plan.md Source Code layout (`src_jl/SSHXXZ/{Core,ED,VQE,QMeasPort,IO}`, `experiments_jl`, `test/{unit,contract,integration}`, `data/`, `figs/`)
- [X] T002 [P] Add Julia dependencies via `Pkg.add` in `Project.toml` (KrylovKit, Yao, BlackBoxOptim, NLopt, NPZ, JSON3) and record `Manifest.toml`
- [X] T003 [P] Create Julia test entry in `test/runtests.jl` (includes unit/contract/integration suites)
- [X] T004 [P] Record Julia env + reproduce command in `env/INTERPRETER_JULIA.md` (`julia --project=. -e 'using Pkg; Pkg.instantiate()'`) and verify imports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: reusable Julia physics/numerics + persistence that every story needs

**⚠️ CRITICAL**: No user story work begins until this phase is complete.
Test tasks T005–T013 MUST be written FIRST and FAIL before T014–T024.

### Tests (write first, FAIL first)

- [X] T005 [P] Unit test Hamiltonian bond placement + OBC + exponential anisotropy in `test/unit/test_hamiltonian.jl` (IV.2; `doc/plan/theory/H.md`)
- [X] T006 [P] Unit test initial-state preparation + P sector membership in `test/unit/test_initial_states.jl` (IV.2)
- [X] T007 [P] Unit test ansatz parameter count/order/halving (δ=0) + F-rule + nesting in `test/unit/test_ansatz.jl` (IV.2)
- [X] T008 [P] Unit test observable evaluation incl ZtR analytic +1/−1/0 in `test/unit/test_observables.jl` (IV.2; XII.3 anchors)
- [X] T009 [P] Unit test physical cost + min-over-branches/restarts selection in `test/unit/test_cost.jl`
- [X] T010 [P] Unit test byte-exact seed-derivation vectors in `test/unit/test_seeds.jl` (contract scan-03-04 §6 encoding)
- [X] T011 [P] Unit test NPZ manifest schema v2 + atomic write + hash idempotency + raw immutability in `test/unit/test_io.jl` (III.6–7; FR-006)
- [X] T012 [P] 5-point 1e-10 QMeasPort-vs-archived-baseline equivalence test in `test/unit/test_qmeas_equivalence.jl` (II.5 paused → D-003 minimal port)
- [X] T013 [P] Unit test free-intercept polyfit post-processing in `test/unit/test_fit.jl` (CL-002 carried over; fit never feeds physics, V.5)

### Implementation (blocking)

- [X] T014 [P] Implement H builder + symmetries in `src_jl/SSHXXZ/Core/Hamiltonian.jl` (`doc/plan/theory/H.md`; sparse + dense paths, no physics redefinition)
- [X] T015 [P] Implement triv/topo/AFM initial states in `src_jl/SSHXXZ/Core/InitialStates.jl` (`doc/plan/theory/psi0.md`)
- [X] T016 [P] Implement S(q)/S(π)/Ostr/Q-derived-only/Z̃R in `src_jl/SSHXXZ/Core/Observables.jl` (`doc/plan/theory/topological_op.md`)
- [X] T017 [P] Implement orbit ansatz circuit in `src_jl/SSHXXZ/Core/Ansatz.jl` (`doc/plan/theory/ansatz.md`; δ=0 halving + AFM-branch GHZ-freeze hooks (first-layer first even sublayer, δ-independent))
- [X] T018 [P] Implement physical cost + branch selection in `src_jl/SSHXXZ/Core/Cost.jl` (`doc/plan/theory/cost_fun.md`)
- [X] T019 [P] Implement sparse production ED (KrylovKit eigsolve tol=1e-10) + dense L≤8 reference in `src_jl/SSHXXZ/ED/Solver.jl` (VIII; dense for cross-validation only)
- [X] T020 Implement minimal QMeasPort (H + initial-state builders only) in `src_jl/SSHXXZ/QMeasPort/Adapter.jl` (D-003; benchmark/random submodules NOT ported)
- [X] T021 [P] Implement NPZ+manifest store + checkpoint/resume in `src_jl/SSHXXZ/IO/Store.jl` (schema `exp01-04/v2`; explicit coordinates; failure states; canonical grids)
- [X] T022 [P] Implement byte-exact seed derivation in `src_jl/SSHXXZ/VQE/Seeds.jl` (SHA256 byte encoding → UInt32)
- [X] T023 Implement ideal optimizer (DE+COBYLA, n_seeds=3, warm start U(−0.3,0.3), n_restarts=3, clamp, θ box) in `src_jl/SSHXXZ/VQE/Optimizer.jl` (`doc/plan/experiment/04_ideal_vqe.md`)
- [X] T024 [P] Implement frozen coordinate grids + q-grid in `src_jl/SSHXXZ/IO/Grids.jl` (49×49 interior, REPS, 49-pt q with π explicit; D_GRID → 2j/50 and AFM rep → (0.5,1.96) amended 2026-10-01 per current doc/)

**Checkpoint**: foundation ready — stories may now proceed (sequentially P1→P4 or in parallel if staffed)

---

## Phase 3: User Story 1 — Exact Phase Structure (Priority: P1) 🎯 MVP

**Goal**: L=8 Z̃R phase diagram on frozen 49×49 grid + δ=0 gaps (L=8,12,16) + scaling fit, all v2

**Independent Test**: SC-001 — rebuild phase diagram, three gap curves, s=0.5 scaling figure from saved v2 data only

### Tests (write first, FAIL first)

- [X] T025 [P] [US1] Contract test 01/02 grid identity in `test/contract/test_grid_01_02.jl` (`contracts/grid-01-02.md` rules 1–5)
- [X] T026 [P] [US1] Integration test SC-001 rebuild-from-data in `test/integration/test_sc001_rebuild.jl`
- [X] T027 [P] [US1] Integration test scaling rebuild consumes v2 gap records + T013 fit in `test/integration/test_sc001_scaling.jl` (CL-002 free intercept, a/b reported)

### Implementation

- [X] T028 [P] [US1] Implement 2401-point Z̃R grid runner in `experiments_jl/exp01_phase.jl` (reads canonical grid; PhaseGridPoint with "(L,s,δ)" + observables + provenance `"source=exact"`)
- [X] T029 [US1] Implement 147-point gap runner (3 L × 49 reused s_i, δ=0, Ls=(8,12,16)) in `experiments_jl/exp01_phase.jl` (R1 spirit; FiniteSizeGapPoint with "(L,s,δ=0,E0,E1,Δraw)"; raw full-Hilbert-space; 26 L=20 records deleted per authorization)
- [X] T030 [P] [US1] Implement scaling post-proc + rebuild scripts in `plotting/diagnostic/exp01.py + plotting/pra/exp01.py` (CL-002 free intercept, report a,b; plotting/post-processing only)

**Checkpoint**: US1 fully functional and independently testable (MVP)

---

## Phase 4: User Story 2 — Observable Characterization (Priority: P2)

**Goal**: heatmaps + 3-representative S(q) (49-pt) with Q derived-only, all v2

**Independent Test**: SC-002 — rebuild S(q) comparison + four heatmaps from saved v2 data only

### Tests (write first, FAIL first)

- [X] T031 [P] [US2] Contract test Q reconstruction-only in `test/contract/test_q_reconstruction.jl` (`contracts/q-reconstruction.md` rules 1–5)
- [X] T032 [P] [US2] Integration test SC-002 rebuild in `test/integration/test_sc002_rebuild.jl`

### Implementation

- [X] T033 [P] [US2] Implement heatmap runner (S(π), Ostr, Q-derived, Z̃R-referenced) in `experiments_jl/exp02_observables.jl` (shares canonical grid + state convention with 01)
- [X] T034 [US2] Implement 3-representative S(q) curves with identical 49-point q array saved per record in `experiments_jl/exp02_observables.jl` (frozen REPS with AFM → (0.5,1.96) amended 2026-10-01; π explicit; distinguishable line styles)
- [X] T035 [P] [US2] Implement rebuild script in `plotting/diagnostic/exp02.py + plotting/pra/exp02.py` (diagnostic + PRA pairs, data-only)

**Checkpoint**: US1 + US2 independently functional

---

## Phase 5: User Story 3 — L=8 Exact Reference (Priority: P3)

**Goal**: 98 exact records (δ=0,0.85) as 04's sole ground truth, v2

**Independent Test**: SC-003 — 98 coordinates present; s-array loadable as 04 authority

### Tests (write first, FAIL first)

- [X] T036 [P] [US3] Contract test 03→04 s authority in `test/contract/test_scan_authority.jl` (AS-03.2; `contracts/scan-03-04.md` rule 1)
- [X] T037 [P] [US3] Integration test SC-003 count in `test/integration/test_sc003_counts.jl`

### Implementation

- [X] T038 [US3] Implement 98-point exact-ref runner in `experiments_jl/exp03_reference.jl` (ExactReferencePoint with "(L=8,s,δ,E0,S_exact(π),O_str,exact)"; `source=exact`)
- [X] T039 [P] [US3] Implement rebuild script in `plotting/diagnostic/exp03.py + plotting/pra/exp03.py` (diagnostic + PRA reference curves, data-only)

**Checkpoint**: all stories so far independently functional

---

## Phase 6: User Story 4 — Ideal Variational Preparation (Priority: P4)

**Goal**: 490 selected + 1470 branch results with frozen optimizer, τ gate, nesting clamp, v2

**Independent Test**: SC-004/SC-005 — counts + 3-branch provenance + Evar≥E0−τ throughout

### Tests (write first, FAIL first)

- [X] T040 [P] [US4] Unit test τ violation flag in `test/unit/test_variational_principle.jl` (AS-04.4)
- [X] T041 [P] [US4] Unit test nesting clamp in `test/unit/test_nesting_clamp.jl` (AS-04.5)
- [X] T042 [P] [US4] Integration test SC-004/005 on mini subset in `test/integration/test_sc004_005.jl`
- [X] T043 [P] [US4] Cross-check test vs archived baseline on mini subset in `test/integration/test_xcheck_mini.jl` (`contracts/xcheck-baseline.md`; E<1e-8/obs<1e-6)

### Implementation

- [X] T044 [US4] Implement 1470 branch-run orchestrator in `experiments_jl/exp04_ideal.jl` (loads 03 s authority; θ box; δ=0 halved (θ1=θ2, no extra deletion); δ=0.85 full params; AFM-branch first-layer first even-sublayer two ZZ frozen 0 independent of scan δ, no expanded freezing from layer 2; byte-exact seeds; n_seeds=3/n_restarts=3; clamp; VariationalBranchResult with "(s,δ,p,initial-state branch)" + θ* + E_branch + `from_baseline∈{0,1}`)
- [X] T045 [US4] Implement argmin selection + exact-record join (orphan rejection) in `experiments_jl/exp04_ideal.jl` (AS-04.2; SelectedVariationalResult links exact coordinates; depends on T044)
- [X] T046 [P] [US4] Implement QS-3 verifier in `experiments_jl/exp04_verify.jl` (reads manifests; asserts 98/490/3-branch/τ/nesting; nonzero exit on failure)
- [X] T047 [P] [US4] Implement comparison rebuild script in `plotting/diagnostic/exp04.py + plotting/pra/exp04.py` (diagnostic + PRA, data-only)

**Checkpoint**: all four stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: validation gates, hashes, timing gate, final compliance — run continuously into production per user rule (no voluntary breakpoints; checkpoints stay)

- [X] T048 [P] Implement SHA256SUMS hash gate in `tools/hash_gate.py` (SC-006 identity; pdf+png pairs; `SOURCE_DATE_EPOCH=0`)
- [X] T049 [P] Execute QS-1–QS-4 validation runs per `specs/002-julia-core-rewrite/quickstart.md` and record outcomes
- [X] T050 Execute representative-subset timing gate and record go/no-go in `specs/002-julia-core-rewrite/subset_timing.md` (VIII.6; gates full launch)
- [X] T051 Implement point-level parallel launcher in `experiments_jl/run_all.jl` (Threads.@threads over points/chains; BLAS single-thread; idempotent resume; deterministic seeds give identical results vs serial; R6)
- [X] T052 Execute full baseline cross-check (5-pt + anchors + per-exp sampling) and record in `specs/002-julia-core-rewrite/xcheck_report.md` (`contracts/xcheck-baseline.md`; mismatch = ERROR gate; PASS 2026-10-01 under D-002-amended contract: builder equivalence 0.0, anchors exact, limits exact, sampling ≤1.2e-13, 04 margins positive)
- [X] T053 Final Constitution Check I–XII + XI/XII absence audit (no finite-shot/hardware/05 content; Python core untouched) recorded in `specs/002-julia-core-rewrite/constitution_check.md` (re-audited 2026-10-01: code hits zero; src/ zero modifications + one shim addition recorded; D-002 operational change recorded)
- [X] T054 Run full Julia test suite green (`Pkg.test()`) and re-run end-to-end validation per quickstart (QS-1–QS-4; PASS 2026-10-01: Pkg.test exit 0, 21 testsets; QS-1/QS-2 hashes green; QS-3 98/490/1470 zero-violation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — starts immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all user stories
- **Stories (Phases 3–6)**: depend on Foundational; then P1→P2→P3→P4 (or parallel if staffed; US3 authority feeds US4 data at runtime, code-independent)
- **Polish (Final Phase)**: depends on all stories complete; T050 timing gate must GO before full production; T051 launcher required for production

### User Story Dependencies

- **User Story 1 (P1)**: after Foundational; no story dependencies — MVP
- **User Story 2 (P2)**: after Foundational; reads US1 canonical grid/Z̃R at runtime, independently testable via fixtures
- **User Story 3 (P3)**: after Foundational; independent
- **User Story 4 (P4)**: after Foundational; consumes US3 s-array + exact records at runtime (contract-tested)

### Within Each Story

Tests MUST be written and FAIL before implementation → core physics before orchestration → orchestration before rebuild scripts → checkpoint per story. Test runs flow continuously into production runs (user rule); checkpoints make every resume safe.

### Parallel Opportunities

- [P] Setup tasks (T002–T004), [P] Foundational tests + implementations (distinct files), per-story [P] tests and rebuild scripts, stories 1–4 in parallel post-foundation if staffed.

---

## Parallel Example: User Story 1

```julia
# Launch US1 tests together (FAIL first):
Task: "Contract test 01/02 grid identity in test/contract/test_grid_01_02.jl"      # T025
Task: "Integration test SC-001 rebuild in test/integration/test_sc001_rebuild.jl" # T026
# Then US1 implementations with distinct files in parallel:
Task: "2401-point Z̃R grid runner in experiments_jl/exp01_phase.jl"                # T028
Task: "Scaling post-proc + rebuild in plotting/diagnostic/exp01.py + plotting/pra/exp01.py"                   # T030
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → 2. Phase 2 Foundational → 3. Phase 3 US1 → **VALIDATE** SC-001 → continue (no voluntary stop per user rule)

### Incremental Delivery

Setup + Foundational → US1 (MVP) → US2 → US3 → US4 → Polish; each increment independently testable; test runs continue into production runs without breakpoints.

### Parallel Team Strategy

Together: Setup + Foundational. Then Developer A: US1, B: US2, C: US3, D: US4 (US4 runtime data depends on US3 outputs via contract, code work parallelizable with fixtures).

---

## Notes

- [P] = different files, no pending dependencies; [USx] maps task to story
- data-model constraints quoted verbatim in task text (no implementation-time discretion)
- Commit after each task or logical group; stop at any checkpoint to validate story independently
- Forbidden: vague tasks, same-file parallel conflicts, cross-story code dependencies, any 05/hardware/shots/backend-abstraction work (XI/XII); Python core files MUST NOT be created, modified, or deleted

---

## Phase 8: Doc-Sync Patch (doc/ 2026-09-30 revision; no physics change)

**Scope notes**: 26 out-of-scope L=20 gap records deleted per 2026-09-30
authorization; gap scope is 147 points (L=8,12,16). T052–T054 stay open
until these patches land.

- [X] T055 Implement canonical basis-vector store + lookup in `src_jl/SSHXXZ/IO/Store.jl` (key includes code_version + H-definition hash; L=8 and L=16 vectors stored in full; `contracts/shared-basis.md` rules 1–5)
- [X] T056 Wire shared-basis reuse into 01/02/03 runners (same $(L,s,\delta)$ loads shared vector, never re-diagonalizes; orchestration-only change, no physics formula touched)
- [X] T057 Sync gap runner default Ls to (8,12,16) in `experiments_jl/exp01_phase.jl` (L=20 records already deleted; 147-point scope)
- [X] T058 [US1] Figure gate G01: US1 data complete → rebuild_01 pairs + hash green → 02 production may start (plan Production Gates; prior Julia-pipeline pass voided 2026-10-01, re-passed under Python plotting/v2read pipeline, hashes green)
- [X] T059 [US2] Figure gate G02: US2 data complete → rebuild_02 pairs + hash green → 03 production may start (re-passed 2026-10-01 post-cleanup under Python plotting/v2read pipeline; sq zombie records deleted after `_, psi` swap bug found+fixed in `run_sq_curves`, recomputed S(π) afm 7.99/topo 2.04/triv 2.02, figures redrawn + hashes double-green)
- [X] T060 [US3] Figure gate G03: US3 data complete → rebuild_03 pairs + hash green → 04 production may start (re-passed 2026-10-01 post-cleanup: prior pass voided on empty dirs; now 3 diag png + 3 pra pdf/png pairs physically in dirs, double-rebuild hashes green)
- [X] T061 [US4] Figure gate G04: verify_04 zero-violation + comparison pairs green → converge (plan Production Gates; passed 2026-10-01: PROD04 sel=490, 0 violations/0 nesting, cmp+ref pairs rebuilt under Python plotting pipeline, double-rebuild hashes green; MIGRATED 2026-10-01 per instruction: 3 cmp pairs out of qs3 into new figs/qs4pra//qs4diag/ as 6 δ-split panels (d0/d085), p color-only no markers; qs3 ref_-only sums rewritten + ref pra_check restored; qs4 double-build green, G04 re-verified under qs4; REVISED 2026-10-01: p=1..3 only, 3 markers/series, δ annotated on-panel, hashes re-greened; INTFMT 2026-10-01: L/p legends int, δ labels :g, qs1/qs3/qs4 rebuilt + hashes green)
- [X] T062 Record 2026-10-01 cleanup (per instruction): stopped all Julia compute (0 procs confirmed; 45 Julia-04 branch records kept); deleted v1 `data/` tree, old `figs/`+`figs_jl/` contents, `scripts_jl/` dir, `tools_jl/hash_gate.jl` (manifest at `reports/cleanup_002.log`, 20886 lines); renamed `data_jl/` → `data/`; plotting back to Python (`plotting/v2read.py` + vendored `pra_style.py` + `pra_check.py` blocks); paths synced in tasks/quickstart/plan/gitignore. Untouched: `src/`, `experiments/`, `tests/`, `src_jl/`, `experiments_jl/`, `test/`, spec, constitution.

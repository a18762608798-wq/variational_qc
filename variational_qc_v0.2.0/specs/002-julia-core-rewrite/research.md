# Research: Julia Core Rewrite (SSH-XXZ 01–04)

**Feature**: `002-julia-core-rewrite` | **Date**: 2026-09-30
**Authority**: spec.md Binding Clarifications (D-001–D-003 frozen) >
`doc/plan` > `theory/`. No physics redefined here.

Phase 0 outcome: **zero NEEDS CLARIFICATION remain**.

## R1 — Solver/optimizer stack (D-001 = A, frozen in clarify)

- **Decision**: KrylovKit.jl `eigsolve` (sparse production ED, tol 1e-10) +
  LinearAlgebra `eigen` dense cross-check (L≤8 only) + Yao.jl ideal
  statevector + BlackBoxOptim.jl adaptive-DE global step + NLopt.jl COBYLA
  polish (mirrors round-1 DE+COBYLA method, incl. n_seeds=3 / n_restarts=3 /
   warm start + U(−0.3,0.3) / clamp / θ box / δ=0 halving / AFM-branch GHZ
   freeze (first-layer first even sublayer, δ-independent) /
   byte-exact seeds).
- **Rationale**: each piece is the ecosystem-standard tool for its job;
  Yao.jl is already pinned by `doc/plan/experiment/04_ideal_vqe.md`; the
  optimizer chain preserves the validated round-1 methodology so depth/branch
  comparisons stay commensurable.
- **Alternatives considered**: ITensors/DMRG-first (B) — rejected: overkill
  for L≤20 exact scope, changes the methodological baseline; hand-rolled
  Lanczos (C) — rejected: unjustified work, worse-tested than KrylovKit.

## R2 — Cross-check tolerance and coverage (D-002 = A, frozen in clarify)

- **Decision**: Julia vs archived Python baseline: energies <1e-8,
  observables <1e-6; coverage = 5-point subset in full + analytic anchors
  (+1/−1/0) + ≥3 sampled points per experiment 01–04. Breach = correctness
  failure, never a result.
- **Rationale**: one order looser than round-1 internal gates (1e-10) to absorb
  cross-language last-ulp drift (ARPACK/Krylov subspace starts, BLAS order),
  still orders tighter than any physics scale; anchors are exact by
  construction.
- **Alternatives considered**: looser-only-subset (B) — rejected: leaves
  per-experiment code paths unverified; bitwise identity (C) — rejected:
  cross-solver bitwise equality is not attainable.

## R3 — qmeas equivalent (D-003 = A, frozen in clarify)

- **Decision**: minimal port — only the H and initial-state builders actually
  called this round, in `QMeasPort/`, locked by the 5-point <1e-10 equivalence
  test (same subset definition as round 1). benchmark/random submodules NOT
  ported.
- **Rationale**: reuses the validated contract surface; full port is
  unrequested work (XI/XII anti-complexity).
- **Alternatives considered**: full port (B) — rejected as speculative;
  zero-code output-compare (C) — rejected: leaves builder-level divergence
  undetectable.

## R4 — Julia environment

- **Decision**: repo-root Julia project env (`Project.toml` + `Manifest.toml`,
  Pkg-managed); `Pkg.instantiate()` reproduces it. Python pixi env retained
  ONLY for plotting/hash tooling.
- **Rationale**: single project, standard Julia reproducibility; no venv/pip
  involved on the Julia side by construction.

## R5 — Storage and provenance (v2)

- **Decision**: per-point `.npz` via NPZ.jl + JSON manifest (JSON3.jl),
  schema `exp01-04/v2`; atomic tmp+rename; provenance block identical in
  spirit to round 1 (experiment/stage, L, params, depth, branch,
  optimizer/backend, seed, code + Manifest versions); backend identities
  `julia-krylovkit` / `julia-yao`.
- **Rationale**: byte-layout identical to v1, so figure/hash tooling and the
  archived-baseline cross-check work unchanged; only the schema string and
  provenance values advance.
- **Alternatives considered**: JLD2 (native, faster) — rejected: breaks
  plotting reuse and cross-language readability; HDF5.jl — rejected: new
  dependency for no measured need.

## R6 — Parallelism and testing (AMENDED: threads, not processes)

- **Decision**: multi-threaded point-level parallelism (`Threads.@threads`,
  `JULIA_NUM_THREADS=N`) over points/chains with the same idempotent-resume
  protocol; BLAS single-threaded (`BLAS.set_num_threads(1)`) against
  oversubscription; serial selection afterwards (cheap). Tests: Test.jl
  stdlib, `test/{unit,contract,integration}/` + `test/runtests.jl` entry;
  TDD FAIL-first per Constitution IV.
- **Rationale**: Distributed.jl multiprocess failed on module-closure
  serialization fragility; threads share memory (better on the memory-tight
  box) and need no serialization at all. Determinism still comes from
  derived seeds, so threaded results equal serial ones.

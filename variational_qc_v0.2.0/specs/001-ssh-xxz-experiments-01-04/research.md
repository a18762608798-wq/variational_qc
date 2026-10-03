# Research: SSH-XXZ Experiments 01–04

**Feature**: `001-ssh-xxz-experiments-01-04` | **Date**: 2026-09-30
**Authority**: spec.md Binding Clarifications (frozen 2026-09-30) > `doc/plan` >
`theory/`. Physics is NOT redefined here; all formulas live in `doc/plan/theory/`.

Phase 0 outcome: **zero NEEDS CLARIFICATION remain**. Each item below records
Decision / Rationale / Alternatives considered.

Interpreter (per `env-python` skill, option A): the repo-local
julia-condapkg-managed env

```text
<repo>/.CondaPkg/.pixi/envs/default/bin/python
```

(Python 3.12.14; numpy 2.5.3, scipy 1.18.1, qiskit 2.5.2, qiskit-aer,
matplotlib 3.11.2, pytest 9.1.1, qmeas 0.1.0 editable — verified by
execution.) No venv, no system pip. Any future dependency (e.g. h5py) MUST go
through `CondaPkg.toml` (julia-condapkg), never pip/venv.

---

## R1 — Gap-curve s-resolution (δ=1 line, AS-01.2)

- **Decision**: gap curves reuse the frozen $s_i=i/50\;(i=1,\dots,49)$ coordinates
  (49 points per $L$). "Complete" in AS-01.2 means all 49 points present
  (record or explicit failure) for each of $L=4,8,12,16$.
- **Rationale**: $\delta=1$ is not on the $49\times49$ mesh ($3j/50=1$ has no integer
  $j$), so the line needs its own ED runs regardless; reusing the frozen $s_i$
  avoids a second grid concept and keeps coordinates consistent with the 03/04
  authoritative $s$ set (FR-009, AS-03.3 spirit).
- **Alternatives considered**: denser 99-point or adaptive refinement near the
  $s\to1$ collapse — rejected: spec does not require it; explicit coordinates in
  the schema allow densification later without migration.

## R2 — q-grid resolution (Story 2 dual constraint; AMENDED 2026-09-30)

- **Decision (current)**: 49 points $q_k=2\pi k/48$, $k=0,\dots,48$ over
  $[0,2\pi]$ ($q=\pi$ at $k=24$, explicit). Identical array for all three
  representative curves, saved per record.
- **Rationale**: user 2026-09-30 readability call — 8 allowed momenta made the
  topological/trivial overlap invisible and curves coarse; 49 continuous points
  keep the binding dual constraint (same coordinates, π explicit) while
  resolving line shapes. $S(q)$ is $2\pi$-periodic, so the duplicated endpoint
  carries no extra physics.
- **Superseded**: $q_n=2\pi n/L$ 8-point grid (same constraint, coarser sampling).
- **Alternatives considered**: dense linspace rejected earlier for adding no
  physics — revisited: the cost is negligible (3 curves) and readability is a
  genuine acceptance factor for the S(q) comparison figure.

## R3 — Variational tolerance (SC-005/AS-04.4) and nesting clamp (AS-04.5)

- **Decision (tolerance)**: violation iff $E_{\rm var} < E_0 - \tau$ with
  $\tau=10^{-6}$ absolute. Tests assert $E_{\rm var}\ge E_0-\tau$ on every selected
  result; any breach is a correctness failure (FR-008 record), never a result.
- **Rationale**: statevector-noiseless setting; COBYLA polish noise is
  $\sim10^{-9}$–$10^{-6}$ while the physics energy scale is $O(1)$; sparse-ED
  reference tolerance is $10^{-10}$, so $\tau$ separates solver noise from real
  violation by orders of magnitude on both sides.
- **Decision (nesting clamp)**: candidate set per $(s,\delta,p)$ =
  {each restart optimum} $\cup$ {embedded $p-1$ baseline: zero-padded new layer,
  freezing/halving rules applied}; accepted = argmin physical energy, with a
  `from_baseline` provenance flag. AS-04.5 holds by construction; test:
  `accepted(p) ≤ baseline(p-1) + τ`.
- **Alternatives considered**: post-hoc check without clamp — rejected: AS-04.5
  requires the baseline be preserved or failure marked; clamp is exactly
  `doc/plan/experiment/04_ideal_vqe.md:29` ("劣于垫底则钳位保留垫底").

## R4 — Solver, qmeas reuse, frozen 04 optimizer, CL-002 fit

- **Decision (ED solver)**: production ED is `scipy.sparse.linalg.eigsh(k=2,
  which='SA', tol=1e-10)` for all sizes ($L\le16$, Constitution VIII);
  dense `numpy.linalg.eigh` is used ONLY for small-$L$ cross-validation
  ($L\le8$ subset, VIII.3) and analytically-known-limit tests (IV.2).
- **Decision (qmeas)**: thin adapter module (`adapters/qmeas_adapter.py`) mapping
  the native call signature onto qmeas Hamiltonian/initial-state builders
  (`doc/plan/experiment/00_data_spec.md`; Constitution II.5). Numerical
  equivalence test over a sample grid: $\max|\Delta E_0|,|\Delta{\rm obs}|
  <10^{-10}$ vs the native builder. If the qmeas API proves incompatible, keep
  the native builder and document — no silent rewrite, no second physics.
- **Decision (04 optimizer, frozen per `doc/plan/experiment/04_ideal_vqe.md`)**:
  $\theta\in[-\pi,\pi]$ box; $p=1$: differential_evolution + COBYLA polish,
  $n_{\rm seeds}=3$; $p\ge2$: warm start from same-$(s,\delta,{\rm init})$
  optimum, new layer $\sim U(-0.3,0.3)$ rad, **$n_{\rm restarts}=3$ (FIXED —
  doc omits the value; 3 chosen symmetric with $n_{\rm seeds}$ and minimal per
  the anti-complexity rule)**; COBYLA polish; clamp per R3; $\delta=1$ halved
  parameters; $\delta=3$ AFM first-layer two ZZ frozen to 0; seeds derived
  deterministically `SHA256(s,δ,init,restart)→uint32` and stored.
- **Decision (CL-002 fit)**: `numpy.polyfit(1/L, Δ, 1)` in post-processing /
  plotting only, reporting $a$ and $b$; fit output never feeds physics
  (Constitution V.5).
- **Alternatives considered**: dense ED at $L=16$ — rejected (VIII.2/3, unnecessary
  $65536^2$ matrix); generic optimizer abstraction — rejected (XI bans
  speculative frameworks; doc freezes the concrete setting).

## R5 — Technical Context (all resolved, no NEEDS CLARIFICATION)

| Slot | Decision |
|------|----------|
| Language | Python, via the repo-local julia-condapkg env above (3.12.14) |
| Dependencies | numpy / scipy / qiskit + qiskit-aer (04 statevector) / matplotlib (figures) / pytest + qmeas 0.1.0 editable (II.5); stdlib json+hashlib for provenance. h5py NOT adopted (see Storage) |
| Storage | per-point `.npz` + JSON manifest, schema `exp01-04/v1` (fields in data-model.md); atomic tmp+rename checkpoint; zero new deps |
| Testing | pytest: `tests/unit` (primitives, IV.2), `tests/contract` (grid/scan/Q contracts), `tests/integration` (idempotent resume, SC rebuild) |
| Target platform | Linux workstation, single-project layout |
| Project type | numerical experiment suite: reusable core lib + orchestration scripts + plotting pipelines |
| Parallelism | `ProcessPoolExecutor` over $(s,\delta)$ points; completed-point short-circuit keyed by config hash; incompatible-config overwrite refused (III.7) |
| Performance estimate | 2401 $L=8$ ED points ($256$-dim, ms-scale) + 2401 observable evals + $4\times49$ gap EDs ($L\le16$ sparse, seconds-scale) + 98 exact-ref + $490\times3$ branch optimizations (dominant cost). Full launch gated on representative-subset timing per VIII.6 |
| Scale | 2401 grid + 196 gap + 98 ref + 1470 branch runs (+490 selected) |

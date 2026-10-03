# Julia Interpreter (project record, T004)

**Environment**: repo-root Julia project env (`Project.toml` + `Manifest.toml`).

**Reproduce**:

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

**Stack** (frozen D-001): KrylovKit.jl (sparse ED), Yao.jl (ideal
statevector), BlackBoxOptim.jl (DE global step), NLopt.jl (COBYLA polish),
NPZ.jl + JSON3.jl (v2 persistence), Test.jl (stdlib).

**Rules**:

- Julia compute lives under `src_jl/`, experiments under `experiments_jl/`,
  tests under `test/` (`test/runtests.jl` entry).
- `src/ssh_xxz` Python core is archived READ-ONLY (XII) — never modified,
  only read or executed as black-box oracle for cross-checks.
- New Julia deps only via `Pkg.add`. No venv/pip on the Julia side.

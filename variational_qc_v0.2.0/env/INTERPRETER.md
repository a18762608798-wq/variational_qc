# Python Interpreter (project record)

**Interpreter (absolute path)** — repo-local julia-condapkg env (option A):

```text
/home/mintusr/sync/theory/physics/contemporary_physics/quant_comp_note/04_project/variational_qc/variational_qc_v0.2.0/.CondaPkg/.pixi/envs/default/bin/python
```

Repo-relative: `.CondaPkg/.pixi/envs/default/bin/python` (built from
`Project.toml` + `CondaPkg.toml` via `Pkg.add("CondaPkg")` then
`CondaPkg.resolve()`).

Python 3.12.14. Verified stack: numpy 2.5.3, scipy 1.18.1, qiskit 2.5.2,
qiskit-aer, matplotlib 3.11.2, pytest 9.1.1, qmeas 0.1.0 (editable,
`../../../03_tools_practice/qmeas`). quarkstudio/quarkcircuit included
pip-side mirroring qmeas's own CondaPkg (needed for `import qmeas`).

**Rules** (per `env-python` skill):

- Use the interpreter above for every run; never system `python3` for project code.
- New dependencies ONLY via `CondaPkg.toml` (julia-condapkg). Forbidden:
  `python3 -m venv`, new `.venv/`/`venv/`, system pip.
- Verify with: `<interp> -c "import numpy,scipy,qiskit,qiskit_aer,matplotlib,pytest"`

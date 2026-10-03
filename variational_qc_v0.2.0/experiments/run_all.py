"""Point-level parallel launcher (T054, R5).

ProcessPoolExecutor over points/chains; each unit is idempotent
(point_exists short-circuit) and deterministic (derived seeds), so parallel
results are bit-identical to serial ones. Selection stays serial (cheap).
"""

from concurrent.futures import ProcessPoolExecutor


def _run_01grid(args):
    data_dir, L, s, d = args
    from experiments.exp01_phase import run_one_grid_point

    return run_one_grid_point(data_dir, L, s, d)


def _run_01gap(args):
    data_dir, L, s = args
    from experiments.exp01_phase import run_one_gap_point

    return run_one_gap_point(data_dir, L, s)


def _run_02heat(args):
    data_dir, L, s, d = args
    from experiments.exp02_observables import run_one_heatmap_point

    return run_one_heatmap_point(data_dir, L, s, d)


def _run_03ref(args):
    data_dir, L, s, d = args
    from experiments.exp03_reference import run_one_ref_point

    return run_one_ref_point(data_dir, L, s, d)


def _run_04chain(args):
    var_dir, L, d, s, branch, depths, de_budget = args
    from experiments.exp04_ideal import run_one_chain

    run_one_chain(var_dir, L, d, s, branch, list(depths), tuple(de_budget))
    return True


def _map(fn, jobs, workers, what):
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for computed in ex.map(fn, jobs):
            done += 1
            if done % 50 == 0:
                print(f"{what}: {done}/{len(jobs)}", flush=True)
    return done


def run_01_grid(data_dir, s_grid, d_grid, L=8, workers=8):
    from experiments.exp01_phase import write_manifest_wrap as _w

    jobs = [(data_dir, L, float(s), float(d)) for s in s_grid for d in d_grid]
    n = _map(_run_01grid, jobs, workers, "exp01grid")
    _w(data_dir, L)
    return n


def run_01_gaps(data_dir, Ls, s_grid, workers=8):
    jobs = [(data_dir, L, float(s)) for L in Ls for s in s_grid]
    return _map(_run_01gap, jobs, workers, "exp01gap")


def run_02_heat(data_dir, s_grid, d_grid, L=8, workers=8):
    from experiments.exp02_observables import write_manifest_wrap as _w

    jobs = [(data_dir, L, float(s), float(d)) for s in s_grid for d in d_grid]
    n = _map(_run_02heat, jobs, workers, "exp02heat")
    _w(data_dir, L)
    return n


def run_03_ref(data_dir, deltas, s_grid, L=8, workers=8):
    from experiments.exp03_reference import write_manifest_wrap as _w

    jobs = [(data_dir, L, float(s), float(d)) for d in deltas for s in s_grid]
    n = _map(_run_03ref, jobs, workers, "exp03ref")
    _w(data_dir, L)
    return n


def run_04_chains(var_dir, ref_dir, deltas, s_grid, branches, depths,
                  de_budget=(300, 10), workers=8):
    """Parallel chains; serial selection afterwards (cheap)."""
    from experiments.exp04_ideal import select_one_point, write_manifest_wrap

    jobs = [(var_dir, 8, float(d), float(s), b, tuple(depths), tuple(de_budget))
            for d in deltas for s in s_grid for b in branches]
    _map(_run_04chain, jobs, workers, "exp04chain")
    n = 0
    for d in deltas:
        for s in s_grid:
            n += select_one_point(var_dir, ref_dir, 8, float(d), float(s),
                                  list(depths), branches=list(branches))
    write_manifest_wrap(var_dir, depths)
    return n

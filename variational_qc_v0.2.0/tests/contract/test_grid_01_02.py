"""T023: 01/02 grid identity contract (grid-01-02 rules 1-5). FAIL-first."""

import numpy as np

from ssh_xxz.io.grids import D_GRID, S_GRID


def test_frozen_grid_values():
    assert len(S_GRID) == 49 and len(D_GRID) == 49
    assert S_GRID[0] == 0.02 and S_GRID[-1] == 0.98
    assert D_GRID[0] == 0.06 and D_GRID[-1] == 2.94
    assert 0.0 not in S_GRID and 1.0 not in S_GRID
    assert 0.0 not in D_GRID and 3.0 not in D_GRID


def test_single_canonical_definition():
    # 01 and 02 must import the same arrays (never regenerate).
    import experiments.exp01_phase as e1
    import experiments.exp02_observables as e2

    assert e1.S_GRID is S_GRID and e2.S_GRID is S_GRID
    assert e1.D_GRID is D_GRID and e2.D_GRID is D_GRID
    assert np.shares_memory(e1.S_GRID, e2.S_GRID)

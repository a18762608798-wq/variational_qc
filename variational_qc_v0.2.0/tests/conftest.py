"""Shared fixtures: frozen grids, temp data dir, interpreter-agnostic paths."""

import numpy as np
import pytest

S_GRID = np.arange(1, 50) / 50.0
D_GRID = 3.0 * np.arange(1, 50) / 50.0
REPS = {
    "trivial": (0.02, 0.06),
    "topological": (0.98, 0.06),
    "afm": (0.50, 2.94),
}
Q_GRID_L8 = 2.0 * np.pi * np.arange(8) / 8.0


@pytest.fixture
def s_grid():
    return S_GRID


@pytest.fixture
def d_grid():
    return D_GRID


@pytest.fixture
def tmp_data_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    return d

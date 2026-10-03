"""CL-002 scaling fit: post-processing ONLY, never feeds physics (V.5)."""

import numpy as np


def fit_scaling(inv_L, gaps):
    """Free-intercept linear fit Δ = a/L + b; returns (a, b)."""
    a, b = np.polyfit(np.asarray(inv_L, dtype=float),
                      np.asarray(gaps, dtype=float), 1)
    return float(a), float(b)

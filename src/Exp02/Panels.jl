# Per-point D04 panel assembly for exp02 (spec POST-002).
# Q = 4/3 + 2 O_str − S(π)/6 (docs/theory/topological_op.md).
# ~Z_R reuses Exp01 read-only (definitional identity with D01).

using Exp01: z_tilde  # top-level reuse (read-only); load Exp01 before Exp02

struct PanelPoint
    s_pi::Float64
    o_str::Float64
    q_val::Float64
    z_tilde::Float64
end

"""Full (Sπ, Ostr, Q, Zt) tuple for one ground-state vector."""
function panel_point(psi::AbstractVector)
    C = zz_correlators(psi)
    s_pi = structure_factor(C, pi)
    o_str = string_order(psi)
    q_val = 4 / 3 + 2 * o_str - s_pi / 6
    zt = z_tilde(psi).z_tilde
    return PanelPoint(s_pi, o_str, q_val, zt)
end


# Experiment 01 orchestration ONLY (Julia round, new H).
# Reads the canonical grid; never reimplements physics. Idempotent resume.

isdefined(Main, :SSHXXZ) ||
    include(joinpath(@__DIR__, "..", "src_jl", "SSHXXZ.jl"))
using .SSHXXZ

const CODE_VERSION = "0.2.0-julia"

_prov(exp, L, backend) = Dict("experiment" => exp, "L" => L,
    "backend" => backend, "seed" => "deterministic-n/a",
    "code_version" => CODE_VERSION, "source" => "exact")

function run_one_grid_point(data_dir, L, s, d)
    rec = Dict("L" => L, "s" => Float64(s), "delta" => Float64(d),
               _prov("exp01", L, "julia-krylovkit")...)
    point_exists(data_dir, "exp01", rec) && return false
    shared = joinpath(dirname(data_dir), "shared")
    try
        psi, e0 = get_or_compute_basis(shared, L, Float64(s), Float64(d), () -> begin
            H = build_hamiltonian(L, Float64(s), Float64(d))
            e0, psi = ground_state(H)
            (psi, e0)
        end; code_version=CODE_VERSION, h_def=H_DEF)
        merge!(rec, Dict("E0" => e0, "ZtR" => z_tilde_R(psi, L), "status" => "ok"))
    catch exc
        merge!(rec, Dict("status" => "failed", "reason" => sprint(showerror, exc)))
    end
    save_point(data_dir, "exp01", rec)
    return true
end

function run_one_gap_point(data_dir, L, s)
    rec = Dict("L" => L, "s" => Float64(s), "delta" => 0.0,
               _prov("exp01gap", L, "julia-krylovkit")...)
    point_exists(data_dir, "exp01gap", rec) && return false
    shared = joinpath(dirname(data_dir), "shared")
    try
        H = build_hamiltonian(L, Float64(s), 0.0)
        e0, e1, psi0, _ = lowest_two(H)
        # Publish the ground state for 03 δ=0 reuse (shared-basis rule 2).
        save_basis(shared, L, Float64(s), 0.0, psi0, e0;
                   code_version=CODE_VERSION, h_def=H_DEF)
        merge!(rec, Dict("E0" => e0, "E1" => e1, "draw" => e1 - e0, "status" => "ok"))
    catch exc
        merge!(rec, Dict("status" => "failed", "reason" => sprint(showerror, exc)))
    end
    save_point(data_dir, "exp01gap", rec)
    return true
end

function run_grid(data_dir; L=8, s_grid=S_GRID, d_grid=D_GRID)
    n = 0
    for s in s_grid, d in d_grid
        n += run_one_grid_point(data_dir, L, Float64(s), Float64(d))
    end
    write_manifest(data_dir, "exp01",
                   Dict("schema" => "exp01-04/v2", "L" => L,
                        "grid" => "49x49-interior", "code_version" => CODE_VERSION))
    return n
end

function run_gaps(data_dir; Ls=(8, 12, 16), s_grid=S_GRID)
    n = 0
    for L in Ls, s in s_grid
        n += run_one_gap_point(data_dir, L, Float64(s))
    end
    return n
end

function write_manifest_wrap(data_dir, L=8)
    write_manifest(data_dir, "exp01",
                   Dict("schema" => "exp01-04/v2", "L" => L,
                        "grid" => "49x49-interior", "code_version" => CODE_VERSION))
end

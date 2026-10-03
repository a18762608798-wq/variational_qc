# Experiment 03 orchestration ONLY (Julia round, new H; scan lines δ=0,0.85).
#
# S_REF is the AUTHORITATIVE s array (AS-03.2): 04 MUST import it
# (contracts/scan-03-04.md rule 1), never regenerate its own grid.

isdefined(Main, :SSHXXZ) ||
    include(joinpath(@__DIR__, "..", "src_jl", "SSHXXZ.jl"))
using .SSHXXZ

const S_REF = collect(1:49) ./ 50.0
const DELTAS = (0.0, 0.85)
const CODE_VERSION = "0.2.0-julia"

_prov() = Dict("experiment" => "exp03", "L" => 8, "backend" => "julia-krylovkit",
    "seed" => "deterministic-n/a", "code_version" => CODE_VERSION, "source" => "exact")

function run_one_ref_point(data_dir, L, s, d)
    rec = Dict("L" => L, "s" => Float64(s), "delta" => Float64(d), _prov()...)
    point_exists(data_dir, "exp03", rec) && return false
    shared = joinpath(dirname(data_dir), "shared")
    try
        psi, e0 = get_or_compute_basis(shared, L, Float64(s), Float64(d), () -> begin
            H = build_hamiltonian(L, Float64(s), Float64(d))
            e0, psi = ground_state(H)
            (psi, e0)
        end; code_version=CODE_VERSION, h_def=H_DEF)
        merge!(rec, Dict("E0" => e0, "Spi" => s_pi(psi, L),
                         "Ostr" => string_order(psi, L), "status" => "ok"))
    catch exc
        merge!(rec, Dict("status" => "failed",
                         "reason" => sprint(showerror, exc)))
    end
    save_point(data_dir, "exp03", rec)
    return true
end

function run_reference(data_dir; L=8, deltas=DELTAS, s_grid=S_REF)
    n = 0
    for d in deltas, s in s_grid
        n += run_one_ref_point(data_dir, L, Float64(s), Float64(d))
    end
    write_manifest(data_dir, "exp03",
                   Dict("schema" => "exp01-04/v2", "L" => L, "scan" => "2x49",
                        "code_version" => CODE_VERSION))
    return n
end

iter_reference(data_dir) =
    [r for r in iter_points(data_dir, "exp03") if r["status"] == "ok"]

function write_manifest_wrap(data_dir, L=8)
    write_manifest(data_dir, "exp03",
                   Dict("schema" => "exp01-04/v2", "L" => L, "scan" => "2x49",
                        "code_version" => CODE_VERSION))
end

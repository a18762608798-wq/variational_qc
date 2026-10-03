# Experiment 02 orchestration ONLY (Julia round, new H).
# Shares canonical grid + state convention with 01; Q derived-only.

isdefined(Main, :SSHXXZ) ||
    include(joinpath(@__DIR__, "..", "src_jl", "SSHXXZ.jl"))
using .SSHXXZ

const CODE_VERSION = "0.2.0-julia"

_prov(L) = Dict("experiment" => "exp02", "L" => L, "backend" => "julia-krylovkit",
    "seed" => "deterministic-n/a", "code_version" => CODE_VERSION, "source" => "exact")

function run_one_heatmap_point(data_dir, L, s, d)
    rec = Dict("L" => L, "s" => Float64(s), "delta" => Float64(d), _prov(L)...)
    point_exists(data_dir, "exp02", rec) && return false
    shared = joinpath(dirname(data_dir), "shared")
    try
        psi, e0 = get_or_compute_basis(shared, L, Float64(s), Float64(d), () -> begin
            H = build_hamiltonian(L, Float64(s), Float64(d))
            e0, psi = ground_state(H)
            (psi, e0)
        end; code_version=CODE_VERSION, h_def=H_DEF)
        spi = s_pi(psi, L)
        ostr = string_order(psi, L)
        merge!(rec, Dict("E0" => e0, "Spi" => spi, "Ostr" => ostr,
                         "Q" => q_diagnostic(spi, ostr),
                         "ZtR" => z_tilde_R(psi, L),
                         "ZtR_ref" => "exp01-canonical", "status" => "ok"))
    catch exc
        merge!(rec, Dict("status" => "failed", "reason" => sprint(showerror, exc)))
    end
    save_point(data_dir, "exp02", rec)
    return true
end

function run_heatmaps(data_dir; L=8, s_grid=S_GRID, d_grid=D_GRID)
    n = 0
    for s in s_grid, d in d_grid
        n += run_one_heatmap_point(data_dir, L, Float64(s), Float64(d))
    end
    write_manifest(data_dir, "exp02",
                   Dict("schema" => "exp01-04/v2", "L" => L,
                        "grid" => "49x49-interior-shared",
                        "code_version" => CODE_VERSION))
    return n
end

function run_sq_curves(data_dir; L=8)
    q = q_grid()
    n = 0
    for (name, (s, d)) in REPS
        rec = Dict("L" => L, "s" => Float64(s), "delta" => Float64(d),
                   "rep" => name, "q" => collect(q), "h_def" => H_DEF, _prov(L)...)
        # Freshness gate (T055 standard): coords match is not enough; a stale
        # code_version/H definition forces recompute instead of zombie reuse.
        if point_exists(data_dir, "exp02sq", rec) &&
           is_fresh_point(data_dir, "exp02sq", rec;
                          code_version=CODE_VERSION, h_def=H_DEF)
            continue
        end
        for stale in (joinpath(data_dir, "exp02sq_$(config_hash(rec)).npz"),
                      joinpath(data_dir, "exp02sq_$(config_hash(rec)).json"))
            isfile(stale) && rm(stale)
        end
        shared = joinpath(dirname(data_dir), "shared")
        try
            psi, _ = get_or_compute_basis(shared, L, Float64(s), Float64(d), () -> begin
                H = build_hamiltonian(L, Float64(s), Float64(d))
                e0, psi = ground_state(H)
                (psi, e0)
            end; code_version=CODE_VERSION, h_def=H_DEF)
            merge!(rec, Dict("Sq" => structure_factor(psi, L, q), "status" => "ok"))
        catch exc
            merge!(rec, Dict("status" => "failed",
                             "reason" => sprint(showerror, exc)))
        end
        save_point(data_dir, "exp02sq", rec)
        n += 1
    end
    return n
end

function write_manifest_wrap(data_dir, L=8)
    write_manifest(data_dir, "exp02",
                   Dict("schema" => "exp01-04/v2", "L" => L,
                        "grid" => "49x49-interior-shared",
                        "code_version" => CODE_VERSION))
end

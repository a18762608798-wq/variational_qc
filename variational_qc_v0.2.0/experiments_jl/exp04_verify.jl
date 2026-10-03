# QS-3 verifier (T046): 03/04 linkage checks over saved manifests.
# Asserts 98 exact / 490 selected / 3-branch provenance / τ / nesting;
# nonzero exit on failure (ERROR gate).

isdefined(Main, :SSHXXZ) ||
    include(joinpath(@__DIR__, "..", "src_jl", "SSHXXZ.jl"))
using .SSHXXZ
include(joinpath(@__DIR__, "exp04_ideal.jl"))

function main_qs3(ref_dir, var_dir; tau=1e-6)
    ref = [r for r in iter_points(ref_dir, "exp03") if r["status"] == "ok"]
    sel = [r for r in iter_points(var_dir, "exp04s")]
    br = [r for r in iter_points(var_dir, "exp04b") if r["status"] == "ok"]
    rep = verify_selection(var_dir, ref_dir; tau=tau)
    ok = (length(ref) == 98 && rep["n_selected"] == 490 &&
          rep["n_violations"] == 0 && rep["n_nesting_violations"] == 0 &&
          length(br) == 490 * 3)
    println("exact=$(length(ref)) selected=$(rep["n_selected"]) " *
            "branches=$(length(br)) violations=$(rep["n_violations"]) " *
            "nesting=$(rep["n_nesting_violations"])")
    return ok ? 0 : 1
end

if abspath(PROGRAM_FILE) == @__FILE__
    ref_dir, var_dir = ARGS[1], ARGS[2]
    exit(main_qs3(ref_dir, var_dir))
end

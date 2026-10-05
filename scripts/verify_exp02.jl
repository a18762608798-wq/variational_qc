# T008 production assertions against the exp02 D03/D04 output.
# Fails (nonzero exit) on any violation.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using Shared01
using Shared01: load_shared01
using NPZ, JSON3

const DATA = joinpath(@__DIR__, "..", "data", "exp02")
failures = String[]

function check(cond::Bool, msg::String)
    cond || push!(failures, msg)
    println((cond ? "PASS " : "FAIL ") * msg)
end

d03 = NPZ.npzread(joinpath(DATA, "exp02_D03.npz"))
d04 = NPZ.npzread(joinpath(DATA, "exp02_D04.npz"))
manifest = open(JSON3.read, joinpath(DATA, "exp02_manifest.json"))

q = vec(d03["q_grid"])
curves = d03["curves"]
check(length(q) == 99 && size(curves) == (3, 99), "D03 shapes (99 q, 3 curves)")
check(abs(q[50] - pi) < 1e-12, "q grid contains pi at k=50")
check(all(curves .>= -1e-12), "S(q) >= -1e-12 (nonnegative)")
check(all(isfinite, curves), "D03 no missing/NaN")

for key in ("s_pi", "o_str", "q_val", "z_tilde")
    v = d04[key]
    check(size(v) == (99, 99) && all(isfinite, v), "D04 panel $key 99x99 finite")
end

# D03<->D04 pi consistency at rep points. NOTE: D03 q[50] (=50*2π/100 in fp)
# need not be bit-identical to π, so this is a tight tolerance, not bit equality.
rep_ij = Dict("trivial" => (1, 1), "topological" => (99, 1), "afm" => (50, 99))
for (r, label) in enumerate(["trivial", "topological", "afm"])
    i, j = rep_ij[label]
    err = abs(curves[r, 50] - d04["s_pi"][i, j])
    check(err < 1e-9, "D03/D04 pi agreement $label err=$err")
end

# Q identity recomputed from stored panels (same ops -> bit-exact).
qres = maximum(abs.(d04["q_val"] .- (4 / 3 .+ 2 .* d04["o_str"] .- d04["s_pi"] / 6)))
check(qres == 0.0, "Q identity bit-exact (res=$qres)")

# D04(d) vs D01: same kernel, same input -> bit-exact.
d01 = NPZ.npzread(joinpath(@__DIR__, "..", "data", "exp01", "exp01_D01.npz"))
check(d04["z_tilde"] == d01["z_tilde"], "D04(d) == D01 bit-exact")

# Degeneracy flags 1:1 with S01.
_, s01_manifest = load_shared01(joinpath(@__DIR__, "..", "data", "shared01"))
s01_deg = Set([(Int(p["grid_index"][1]), Int(p["grid_index"][2]))
               for p in s01_manifest["degenerate_points"]])
d04_deg = Set([(i, j) for j in 1:99 for i in 1:99 if d04["degenerate"][i, j]])
check(s01_deg == d04_deg, "degeneracy flags 1:1 ($(length(d04_deg)) points)")

if isempty(failures)
    println("VERIFY-EXP02-OK")
else
    println("VERIFY-EXP02-FAILURES: ", length(failures))
    exit(1)
end

# T007 diagnostics (record only, no pass/fail thresholds; physical
# interpretation belongs to exp01/exp02).
# 1. Overlap of the leftmost column (s=0.01) with the s=0 odd-bond singlet
#    product state (docs/theory/psi0.md).
# 2. Writes data/shared01/diagnostics.json.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using Shared01
using Shared01: load_shared01
using LinearAlgebra, JSON3

const DATA = joinpath(@__DIR__, "..", "data", "shared01")

function singlet_product_state(L::Integer)
    pair = ComplexF64[0, 1, -1, 0] ./ sqrt(2.0)  # (|01>-|10>)/√2, sign irrelevant for |.|^2
    v = pair
    for _ in 2:(L ÷ 2)
        v = kron(v, pair)
    end
    return v
end

function main()
    arrays, _ = load_shared01(DATA)
    E0, psi = arrays["E0"], arrays["psi"]
    triv = singlet_product_state(8)
    @assert length(triv) == 256
    ov = [abs(dot(triv, Vector{ComplexF64}(psi[1, j, :]))) for j in 1:99]
    println("left-column overlap: min=$(minimum(ov)) median=$(sort(ov)[50]) max=$(maximum(ov))")
    open(joinpath(DATA, "diagnostics.json"), "w") do io
        JSON3.write(io, Dict(
            "left_column_s" => 0.01,
            "reference_state" => "odd-bond singlet product (s=0 limit)",
            "overlap_min" => minimum(ov),
            "overlap_median" => sort(ov)[50],
            "overlap_max" => maximum(ov),
            "overlap_per_delta" => ov,
            "note" => "diagnostic only; no threshold asserted (see spec §5)",
        ))
    end
    println("wrote diagnostics.json")
end

main()

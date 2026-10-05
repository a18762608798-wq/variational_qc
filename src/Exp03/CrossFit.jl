# Crossing localization + linear fit for exp03 D02 (spec PRE-003, PRE-004).
# Crossings: strict sign-change bracketings of A1-A2 on the shared (ii) grid,
# s-coordinate by linear interpolation between the bracketing neighbors (Q5).
# Fit: least squares line Δ = a·(1/L) + b (Q4). Pure kernels, no I/O.

module CrossFit

export crossings, linear_fit

"""All pairwise-curve crossings as (s_cross, A_cross) via neighbor interpolation."""
function crossings(s::AbstractVector, A1::AbstractVector, A2::AbstractVector)
    n = length(s)
    (n == length(A1) == length(A2)) || throw(ArgumentError("grid/curve length mismatch"))
    n ≥ 2 || throw(ArgumentError("need at least 2 grid points"))
    out = Tuple{Float64,Float64}[]
    d = Float64.(A1) .- Float64.(A2)
    for t in 1:(n - 1)
        d[t] * d[t + 1] < 0 || continue  # strict bracketing only
        f = -d[t] / (d[t + 1] - d[t])
        sc = Float64(s[t]) + f * (Float64(s[t + 1]) - Float64(s[t]))
        Ac = Float64(A1[t]) + f * (Float64(A1[t + 1]) - Float64(A1[t]))
        push!(out, (sc, Ac))
    end
    return out
end

"""Least squares line ys = a·xs + b; returns (a, b)."""
function linear_fit(xs::AbstractVector, ys::AbstractVector)
    (length(xs) == length(ys) && length(xs) ≥ 2) ||
        throw(ArgumentError("need ≥2 paired points for a fit"))
    X = hcat(Float64.(xs), ones(length(xs)))
    c = X \ Float64.(ys)
    return (a=c[1], b=c[2])
end

end # module

# Schema-versioned per-point persistence. Schema exp01-04/v2.
#
# Layout: <exp>_<hash>.npz (numeric arrays, NPZ.jl) + <exp>_<hash>.json
# (scalars/meta/strings). Atomic tmp+rename; idempotent reruns (III.7);
# tolerance-based scientific equality (ARPACK/Krylov last-ulp lesson).

module Store

using NPZ, JSON3, SHA, Printf

export save_point, load_point, point_exists, write_manifest, config_hash,
       iter_points, SCHEMA, save_basis, load_basis, get_or_compute_basis,
       is_fresh_point

const SCHEMA = "exp01-04/v2"
const COORD_KEYS = ("L", "s", "delta", "p", "branch", "init", "restart",
                    "seed", "q", "exp")

_canon(v::AbstractArray) = vec(collect(Float64, vec(v)))
_canon(v::Complex) = [real(v), imag(v)]
_canon(v::Real) = Float64(v)
_canon(v) = string(v)

function _fmt(k, v)
    vs = k in ("s", "delta", "E0", "E1") && v isa Real ?
         @sprintf("%.17g", Float64(v)) : string(_canon(v))
    return "\"$k\":$vs"
end

function config_hash(rec)
    coords = sort!([(k, rec[k]) for k in keys(rec) if string(k) in COORD_KEYS],
                   by=first)
    s = "{" * join([_fmt(string(k), v) for (k, v) in coords], ",") * "}"
    d = sha256(Vector{UInt8}(codeunits(s)))
    return bytes2hex(d)[1:16]
end

_pointpath(dir, exp, rec) = joinpath(dir, "$(exp)_$(config_hash(rec)).npz")
_metapath(dir, exp, rec) =
    joinpath(dir, "$(exp)_$(config_hash(rec)).json")

function save_point(dir, exp, rec)
    mkpath(dir)
    npz, js = _pointpath(dir, exp, rec), _metapath(dir, exp, rec)
    if isfile(npz) && isfile(js)
        old = load_point(npz)
        _records_equal(old, rec) && return npz
        throw(ArgumentError("incompatible result for $npz; refusing overwrite"))
    end
    arrs = Dict{String,Any}()
    meta = Dict{String,Any}()
    for (k, v) in rec
        ks = string(k)
        if v isa AbstractArray && eltype(v) <: Complex
            # Convention: complex arrays stored as [re..., im...] + length flag.
            arrs[ks] = vcat(real.(vec(collect(v))), imag.(vec(collect(v))))
            meta["__complex__$(ks)"] = length(vec(collect(v)))
        elseif v isa AbstractArray
            arrs[ks] = collect(v)
        elseif v isa Complex
            arrs[ks] = [real(v), imag(v)]
            meta["__complex__$(ks)"] = 1
        else
            meta[ks] = v isa Real ? Float64(v) : string(v)
        end
    end
    tmpn, tmpj = npz * ".part", js * ".part"
    isempty(arrs) && (arrs["__payload_empty__"] = [0.0])  # NPZ.jl rejects empty dicts
    npzwrite(tmpn, arrs)
    open(tmpj, "w") do fh
        JSON3.write(fh, meta)
    end
    mv(tmpn, npz; force=true)
    mv(tmpj, js; force=true)
    return npz
end

function load_point(npzpath)
    d = Dict{String,Any}(string(k) => v for (k, v) in npzread(npzpath))
    js = replace(npzpath, r"\.npz$" => ".json")
    meta = Dict{String,Any}(string(k) => v
                            for (k, v) in JSON3.read(read(js, String)))
    out = Dict{String,Any}()
    for (k, v) in d
        k == "__payload_empty__" && continue
        flag = "__complex__$(k)"
        if haskey(meta, flag)
            n = Int(meta[flag])
            arr = vec(collect(v))
            out[k] = ComplexF64.(arr[1:n] .+ im .* arr[(n + 1):end])
            delete!(meta, flag)
        else
            out[k] = v
        end
    end
    return merge(meta, out)
end

point_exists(dir, exp, rec) =
    isfile(_pointpath(dir, exp, rec)) && isfile(_metapath(dir, exp, rec))

function is_fresh_point(dir, exp, rec; code_version, h_def)
    # T055-standard gate: same coordinates are NOT enough — the stored record
    # must also carry the current code_version AND H definition, otherwise a
    # formula fix silently reuses zombie records (exp02sq 2026-10-01 lesson).
    !point_exists(dir, exp, rec) && return false
    old = load_point(_pointpath(dir, exp, rec))
    return get(old, "code_version", nothing) == string(code_version) &&
           get(old, "h_def", nothing) == string(h_def)
end

function write_manifest(dir, exp, meta)
    mkpath(dir)
    name = "$(exp)_manifest.json"
    open(joinpath(dir, name), "w") do fh
        JSON3.write(fh, meta)
    end
    return name
end

function iter_points(dir, exp)
    out = []
    for f in sort(readdir(dir; join=true))
        endswith(f, ".npz") && startswith(basename(f), "$(exp)_") || continue
        push!(out, load_point(f))
    end
    return out
end

function _records_equal(a, b; rtol=1e-9, atol=1e-12)    Set(keys(a)) == Set(keys(b)) || return false
    for k in keys(a)
        va, vb = a[k], b[k]
        if va isa AbstractArray || vb isa AbstractArray
            # NPZ roundtrip may change 1D <-> (n,1) shape: compare flattened
            # values (length must match); shapes are not scientifically salient.
            aa, bb = vec(collect(va)), vec(collect(vb))
            length(aa) == length(bb) || return false
            if eltype(aa) <: Complex || eltype(bb) <: Complex ||
               eltype(aa) <: AbstractFloat
                isapprox(aa, bb; rtol=rtol, atol=atol) || return false
            else
                aa != bb && return false
            end
        elseif va isa Real || vb isa Real
            isapprox(Float64(va), Float64(vb); rtol=rtol, atol=atol) || return false
        elseif va != vb
            return false
        end
    end
    return true
end

# --- Canonical shared ground-state basis (contracts/shared-basis.md) ---
#
# Key = (L, s, δ, code_version, h_def): same coordinates under a different
# code or physics version MUST NOT alias. Independent hash path so existing
# point records are unaffected. Reuse changes no physics (same H ground state).

function _basis_hash(L, s, delta, code_version, h_def)
    raw = "L=$(L)|s=$(@sprintf("%.17g", Float64(s)))|d=$(@sprintf("%.17g", Float64(delta)))|code=$(code_version)|h=$(h_def)"
    return bytes2hex(sha256(Vector{UInt8}(codeunits(raw))))[1:16]
end

function save_basis(dir, L, s, delta, psi, E0; code_version, h_def)
    mkpath(dir)
    h = _basis_hash(L, s, delta, code_version, h_def)
    npz, js = joinpath(dir, "shared_$(h).npz"), joinpath(dir, "shared_$(h).json")
    if isfile(npz) && isfile(js)
        return npz  # already stored; first writer wins (identical content)
    end
    rec = Dict("L" => L, "s" => Float64(s), "delta" => Float64(delta),
               "code_version" => string(code_version), "h_def" => string(h_def),
               "psi" => Vector{ComplexF64}(vec(collect(psi))), "E0" => Float64(E0))
    tmpn, tmpj = npz * ".part", js * ".part"
    npzwrite(tmpn, Dict("psi" => vcat(real.(rec["psi"]), imag.(rec["psi"]))))
    open(tmpj, "w") do fh
        JSON3.write(fh, Dict("L" => L, "s" => Float64(s), "delta" => Float64(delta),
                             "code_version" => string(code_version),
                             "h_def" => string(h_def), "E0" => Float64(E0),
                             "n" => length(rec["psi"]), "kind" => "shared-basis"))
    end
    mv(tmpn, npz; force=true)
    mv(tmpj, js; force=true)
    return npz
end

function load_basis(dir, L, s, delta; code_version, h_def)
    h = _basis_hash(L, s, delta, code_version, h_def)
    npz, js = joinpath(dir, "shared_$(h).npz"), joinpath(dir, "shared_$(h).json")
    (!isfile(npz) || !isfile(js)) && return nothing
    meta = Dict{String,Any}(string(k) => v for (k, v) in JSON3.read(read(js, String)))
    meta["code_version"] == string(code_version) || return nothing
    meta["h_def"] == string(h_def) || return nothing
    arr = vec(collect(first(values(npzread(npz)))))
    n = Int(meta["n"])
    psi = ComplexF64.(arr[1:n] .+ im .* arr[(n + 1):end])
    return (psi, Float64(meta["E0"]))
end

function get_or_compute_basis(dir, L, s, delta, compute; code_version, h_def)
    hit = load_basis(dir, L, s, delta; code_version=code_version, h_def=h_def)
    hit !== nothing && return (hit[1], hit[2])
    psi, E0 = compute()
    save_basis(dir, L, s, delta, psi, E0; code_version=code_version, h_def=h_def)
    return (Vector{ComplexF64}(vec(collect(psi))), Float64(E0))
end

end # module

# Orbit ansatz (Yao.jl). Authoritative: doc/plan/theory/ansatz.md.
#
# Yao little-endian verified: qubit m <-> site m (bit m-1). Reflection pairs
# share angles; δ=0 halves (θ1=θ2); F-rule sublayer order; fixed F1,S1,...;
# new layers append at END (nesting via zero-pad).

module Ansatz

using Yao

using Yao

export n_params, first_sublayer, layer_order, sublayer_seq,
       build_ansatz_circuit, full_circuit, embed_params

const _FIRST = Dict("trivial" => "e", "topological" => "o", "afm" => "e")

function _orbits(L)
    M = L ÷ 2
    odd, even = [], []
    seen_o, seen_e = Set(), Set()
    for jj in 1:M
        pair = sort([(2j - 1, 2j) for j in (jj, M + 1 - jj)])
        key = Tuple(unique(pair))  # unique kills self-mirror doubles
        key ∉ seen_o && (push!(seen_o, key); push!(odd, collect(key)))
    end
    for jj in 1:(M - 1)
        pair = sort([(2j, 2j + 1) for j in (jj, M - jj)])
        key = Tuple(unique(pair))
        key ∉ seen_e && (push!(seen_e, key); push!(even, collect(key)))
    end
    return odd, even
end

n_params(L, p, delta) = (delta == 0 ? L ÷ 2 : L) * p

layer_order(init) = (f = _FIRST[init]; [f, f == "e" ? "o" : "e"])

first_sublayer(init) = layer_order(init)[1]

function sublayer_seq(L, p, init)
    f, s = layer_order(init)
    return [k % 2 == 1 ? f : s for k in 1:(2p)]
end

_rxx(t) = (c = cos(t / 2); s = sin(t / 2);
    ComplexF64[c 0 0 -im * s; 0 c -im * s 0; 0 -im * s c 0; -im * s 0 0 c])
_ryy(t) = (c = cos(t / 2); s = sin(t / 2);
    ComplexF64[c 0 0 im * s; 0 c -im * s 0; 0 -im * s c 0; im * s 0 0 c])
_rzz(t) = Matrix(Diagonal(ComplexF64[exp(-im * t / 2), exp(im * t / 2),
                                        exp(im * t / 2), exp(-im * t / 2)]))

function _apply_bond!(circ, L, (a, b), t1, t2)
    push!(circ, put(L, (a, b) => matblock(_rxx(t1))))
    push!(circ, put(L, (a, b) => matblock(_ryy(t1))))
    push!(circ, put(L, (a, b) => matblock(_rzz(t2))))
end

function build_ansatz_circuit(L, p, delta, init, theta)
    theta = collect(Float64, theta)
    odd, even = _orbits(L)
    sub = Dict("o" => odd, "e" => even)
    per = delta == 0 ? L ÷ 2 : L
    length(theta) == per * p || throw(ArgumentError("expected $(per*p) params"))
    circ = chain(L)
    k = 0
    for _ in 1:p, kind in layer_order(init)
        for orb in sub[kind]
            if delta == 0
                k += 1
                t1 = t2 = theta[k]
            else
                t1, t2 = theta[k + 1], theta[k + 2]
                k += 2
            end
            for bond in orb
                _apply_bond!(circ, L, bond, t1, t2)
            end
        end
    end
    return circ
end

function _prep_gates!(circ, L, init)
    if init in ("trivial", "topological")
        pairs = init == "trivial" ? [(2j - 1, 2j) for j in 1:(L ÷ 2)] :
                vcat([(1, L)], [(2j, 2j + 1) for j in 1:(L ÷ 2 - 1)])
        for (a, b) in pairs
            push!(circ, put(L, b => X))
            push!(circ, put(L, a => H))
            push!(circ, control(L, a, b => X))
            push!(circ, put(L, a => Z))
        end
    else # afm GHZ: X evens, H_1, CNOT cascade
        for m in 2:2:L
            push!(circ, put(L, m => X))
        end
        push!(circ, put(L, 1 => H))
        for m in 1:(L - 1)
            push!(circ, control(L, m, m + 1 => X))
        end
    end
    return circ
end

function full_circuit(L, p, delta, init, theta)
    circ = chain(L)
    _prep_gates!(circ, L, init)
    return chain(circ, build_ansatz_circuit(L, p, delta, init, theta))
end

embed_params(th, L, p, delta, init) =
    vcat(collect(Float64, th), zeros(n_params(L, 1, delta)))

end # module

# Unit tests for shared-01 and exp01 (T006 each).
# Full-grid assertions run against production outputs via
# scripts/verify_production.jl (shared-01) and scripts/verify_exp01.jl (exp01).

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using Shared01
using Exp01
using Exp03
using LinearAlgebra, Test, NPZ, JSON3

@testset "bonds" begin
    @test odd_bonds(8) == [(1, 2), (3, 4), (5, 6), (7, 8)]
    @test even_bonds(8) == [(2, 3), (4, 5), (6, 7)]
    @test_throws ArgumentError build_hamiltonian(7, 0.5, 0.0)
end

@testset "hamiltonian hermiticity (exact)" begin
    for (s, d) in [(0.01, 0.02), (0.5, 1.0), (0.99, 1.98), (1 - 1e-9, 2 - 1e-9)]
        H = build_hamiltonian(8, s, d)
        @test size(H) == (256, 256)
        @test H == adjoint(H)
    end
end

@testset "grid definition (shared-01 PRE-002)" begin
    @test length(S_GRID) == 99 && length(DELTA_GRID) == 99
    @test S_GRID[1] == 0.01 && S_GRID[end] == 0.99
    @test DELTA_GRID[1] == 0.02 && DELTA_GRID[end] == 1.98
    @test S_GRID[50] == 0.50  # AFM rep column is the middle column
end

@testset "solve_point correctness" begin
    for (s, d) in [(0.01, 0.02), (0.5, 1.0), (0.99, 0.02)]
        sol = solve_point(s, d)
        @test sol.E1 >= sol.E0
        @test norm(sol.psi0) ≈ 1.0
        H = build_hamiltonian(8, s, d)
        res = norm(H * sol.psi0 - sol.E0 * sol.psi0) / max(1.0, norm(H))
        @test res < 1e-8
        @test sol.degenerate == ((sol.E1 - sol.E0) < DEGENERACY_TOL)
    end
end

@testset "rep points are grid points" begin
    for label in REP_LABELS
        s, d = REP_POINTS[label]
        i = round(Int, 100 * s)
        j = round(Int, 50 * d)
        @test S_GRID[i] == s && DELTA_GRID[j] == d
    end
end

@testset "npz complex round-trip (small)" begin
    dir = mktempdir()
    a = rand(ComplexF64, 4, 5)
    NPZ.npzwrite(joinpath(dir, "t.npz"), Dict("psi" => a))
    b = NPZ.npzread(joinpath(dir, "t.npz"))
    @test b["psi"] == a
end

@testset "point_at lookup" begin
    arrays = Dict("E0" => [1.0 2.0; 3.0 4.0], "E1" => [1.1 2.1; 3.1 4.1],
                  "psi" => zeros(ComplexF64, 2, 2, 256))
    # NOTE: point_at enforces exact grid membership on the real 99x99 arrays;
    # here only the off-grid error path is unit-testable without full output.
    @test_throws ArgumentError point_at(arrays, 0.005, 0.02)
    @test_throws ArgumentError point_at(arrays, 0.5, 2.0)  # boundary excluded
end

@testset "exp01 partial trace" begin
    using Exp01
    # Product |0>^8 -> rho on any subsystem is the pure |0..0> projector.
    psi0 = zeros(ComplexF64, 256)
    psi0[1] = 1.0
    rho = Matrix(reduced_density_matrix(psi0, [3, 4, 5, 6]))
    @test size(rho) == (16, 16)
    @test rho == adjoint(rho)
    @test tr(rho) ≈ 1.0
    @test rho[1, 1] ≈ 1.0 && norm(rho - Diagonal(diag(rho))) < 1e-15
    # Singlet on (1,2) x |0>^6: tracing to (1,2) gives the maximally mixed pair.
    s = ComplexF64[0, 1, -1, 0] ./ sqrt(2.0)
    rest = zeros(ComplexF64, 64)
    rest[1] = 1.0
    psi = kron(rest, s)  # sites (1,2) fastest
    rho12 = Matrix(reduced_density_matrix(psi, [1, 2]))
    @test tr(rho12) ≈ 1.0
    @test rho12 ≈ [0 0 0 0; 0 0.5 -0.5 0; 0 -0.5 0.5 0; 0 0 0 0]
    @test_throws ArgumentError reduced_density_matrix(psi0[1:100], [1, 2])
end

@testset "exp01 mirror involution" begin
    using Exp01
    R = mirror_operator()
    @test R * R == I(16)
    @test R == adjoint(R)
end

@testset "exp01 z_tilde sanity (S02)" begin
    using Exp01
    arrays, _ = load_shared01(joinpath(@__DIR__, "..", "data", "shared01"))
    for (s, d) in [(0.01, 0.02), (0.99, 0.02), (0.50, 1.98)]
        i, j = round(Int, 100 * s), round(Int, 50 * d)
        r = z_tilde(Vector{ComplexF64}(arrays["psi"][i, j, :]))
        @test isfinite(r.z_tilde) && r.denom > 1e-12
        @test abs(r.rho_trace - 1.0) < 1e-10 && r.rho_min_eig > -1e-10
    end
end

@testset "exp01 S01 input gate" begin
    using Exp01
    using Exp01: EXPECTED_BASIS_CONVENTION
    good = Dict("schema" => "shared01/v1",
                "basis_convention" => EXPECTED_BASIS_CONVENTION,
                "degenerate_points" => [])
    @test assert_s01_gate(good, EXPECTED_BASIS_CONVENTION) == Set{Tuple{Int,Int}}()
    bad_schema = Dict("schema" => "other/v9",
                      "basis_convention" => EXPECTED_BASIS_CONVENTION,
                      "degenerate_points" => [])
    @test_throws ErrorException assert_s01_gate(bad_schema, EXPECTED_BASIS_CONVENTION)
    bad_basis = Dict("schema" => "shared01/v1", "basis_convention" => "MSB = site 1",
                     "degenerate_points" => [])
    @test_throws ErrorException assert_s01_gate(bad_basis, EXPECTED_BASIS_CONVENTION)
end

@testset "exp02 correlators" begin
    using Exp02
    psi0 = zeros(ComplexF64, 256)
    psi0[1] = 1.0
    C = zz_correlators(psi0)
    @test C == ones(8, 8)
    @test structure_factor(C, 0.0) ≈ 8.0
    @test structure_factor(C, pi) ≈ 0.0 atol = 1e-12
    # singlet on (1,2): C_12 = -1, rest with |0> background
    s = ComplexF64[0, 1, -1, 0] ./ sqrt(2.0)
    rest = zeros(ComplexF64, 64)
    rest[1] = 1.0
    C2 = zz_correlators(kron(rest, s))
    @test C2[1, 2] ≈ -1.0 && C2[2, 1] ≈ -1.0
    @test all(diag(C2) .== 1.0)
    @test_throws ArgumentError zz_correlators(psi0[1:100])
end

@testset "exp02 string order" begin
    using Exp02
    psi0 = zeros(ComplexF64, 256)
    psi0[1] = 1.0
    @test string_order(psi0) ≈ 4.0
    ghz = zeros(ComplexF64, 256)
    ghz[0b10101010 + 1] = 1 / sqrt(2)
    ghz[0b01010101 + 1] = 1 / sqrt(2)
    @test string_order(ghz) ≈ 0.0 atol = 1e-12
    @test_throws ArgumentError string_order(psi0, 6)
end

@testset "exp02 panels Q identity" begin
    using Exp02
    using Shared01
    arrays, _ = load_shared01(joinpath(@__DIR__, "..", "data", "shared01"))
    for (s, d) in [(0.01, 0.02), (0.5, 1.0), (0.99, 0.02)]
        i, j = round(Int, 100 * s), round(Int, 50 * d)
        p = panel_point(Vector{ComplexF64}(arrays["psi"][i, j, :]))
        @test p.q_val ≈ 4 / 3 + 2 * p.o_str - p.s_pi / 6
        @test isfinite(p.s_pi) && isfinite(p.z_tilde)
    end
end

@testset "exp03 sector basis constructive" begin
    using Exp03
    using Exp03: union_points, key_wide, key_narrow
    for L in (8, 12, 16)
        b = sector_basis(L)
        @test length(b.members) > 0
        total = 0
        for (a, mem) in enumerate(b.members)
            for x in mem
                @test count_ones(x) == L ÷ 2
                @test b.index[x] == a
                total += 1
            end
        end
        @test total == binomial(L, L ÷ 2)  # every Z_tot=0 string in exactly one orbit
    end
    # Full-space +symmetry of a random sector vector (L=8).
    b8 = sector_basis(8)
    c = [0.3, -0.7, 0.1, 0.5, -0.2, 0.9, 0.4, -0.6, 0.8, 0.15,
         -0.35, 0.65, -0.45, 0.25, -0.75, 0.55, 0.05, -0.95, 0.85, -0.05,
         0.12, -0.22, 0.33]
    @test length(b8.members) == length(c)
    w = zeros(ComplexF64, 256)
    for (a, mem) in enumerate(b8.members)
        for x in mem
            w[x + 1] += c[a] / sqrt(length(mem))
        end
    end
    for x in UInt64(0):UInt64(255)
        @test w[x + 1] ≈ w[flip_all(x, 8) + 1]
        @test w[x + 1] ≈ w[reflect_bits(x, 8) + 1]
    end
    @test_throws ArgumentError sector_basis(7)
    @test_throws ArgumentError sector_basis(28)  # MAX_L=26 resource guard
end

@testset "exp03 sector hamiltonian vs independent kron path (L=8)" begin
    using Exp03
    using Exp03
    # Independent operators via kron (site m <-> bit (m-1), LSB = site 1).
    Z = ComplexF64[1 0; 0 -1]
    X = ComplexF64[0 1; 1 0]
    I2 = ComplexF64[1 0; 0 1]
    op_at(P, m) = kron([(i == m) ? P : I2 for i in 8:-1:1]...)
    Ztot = sum(op_at(Z, m) for m in 1:8)
    Xbar = kron(fill(X, 8)...)
    Rmat = zeros(ComplexF64, 256, 256)
    for x in UInt64(0):UInt64(255)
        Rmat[reflect_bits(x, 8) + 1, x + 1] = 1.0
    end
    H = build_hamiltonian(8, 0.5, 0.0)
    # H preserves the independently defined symmetric subspace.
    @test norm(H * Xbar - Xbar * H) < 1e-8 * norm(H)
    @test norm(H * Rmat - Rmat * H) < 1e-8 * norm(H)
    @test norm(H * Ztot - Ztot * H) < 1e-8 * norm(H)
    # Sector dimension == rank of the independent projector onto P=-2.
    mask = [count_ones(UInt64(b)) == 4 for b in 0:255]
    idx = findall(mask)
    X70 = Xbar[idx, idx]
    R70 = Rmat[idx, idx]
    Pi70 = (I(70) + X70) * (I(70) + R70) / 4
    @test sum(abs.(eigvals(Hermitian(Pi70)) .- 1.0) .< 1e-8) ==
          length(sector_basis(8).members)
    # Matrix-element spot check: tested assembly vs full-space bra-kets.
    Hs = Matrix(sector_hamiltonian(8, 0.5, 0.0))
    @test norm(Hs - adjoint(Hs)) < 1e-12
    mem = sector_basis(8).members
    function fullvec(a)
        v = zeros(ComplexF64, 256)
        for x in mem[a]
            v[x + 1] = 1 / sqrt(length(mem[a]))
        end
        return v
    end
    for (a1, a2) in [(1, 1), (1, 5), (3, 17), (23, 23)]
        @test dot(fullvec(a1), H * fullvec(a2)) ≈ Hs[a1, a2] atol = 1e-10
    end
    # Gap smoke + determinism.
    r1 = solve_gap(8, 0.5)
    r2 = solve_gap(8, 0.5)
    @test isfinite(r1.delta_gap) && r1.delta_gap ≥ -1e-12
    @test r1.delta_gap ≈ r2.delta_gap atol = 1e-10  # iterative solver: tight, not bitwise
    @test_throws ArgumentError solve_gap(7, 0.5)
end

@testset "exp03 L=12 sector preservation via full H" begin
    using Exp03
    L = 12
    H = build_hamiltonian(L, 0.5, 0.0)
    b = sector_basis(L)
    n = length(b.members)
    c = [sin(1.7a) for a in 1:n]
    v = zeros(ComplexF64, 1 << L)
    for (a, mem) in enumerate(b.members)
        for x in mem
            v[x + 1] += c[a] / sqrt(length(mem))
        end
    end
    w = H * v
    scale = maximum(abs, w)
    for x in UInt64(0):UInt64((1 << L) - 1)
        if count_ones(x) != L ÷ 2
            @test abs(w[x + 1]) < 1e-8 * scale  # magnetization preserved
        else
            @test w[x + 1] ≈ w[flip_all(x, L) + 1] rtol = 1e-8
            @test w[x + 1] ≈ w[reflect_bits(x, L) + 1] rtol = 1e-8
        end
    end
end

@testset "exp03 crossfit synthetic" begin
    using Exp03
    s = collect(0.45:0.0015:0.6)[1:99]
    A1 = 2.0 .* s .- 0.9
    A2 = -1.0 .* s .+ 0.6
    cs = crossings(s, A1, A2)
    @test length(cs) == 1
    @test cs[1][1] ≈ 0.5 atol = 1e-12
    @test cs[1][2] ≈ 0.1 atol = 1e-12
    @test isempty(crossings(s, A1, copy(A1)))
    # Collinear three points: exact recovery.
    fit = linear_fit([1 / 8, 1 / 12, 1 / 16], [3 / 8 + 0.5, 3 / 12 + 0.5, 3 / 16 + 0.5])
    @test fit.a ≈ 3.0 && fit.b ≈ 0.5
    @test_throws ArgumentError crossings(s, A1, A1[1:50])
    @test_throws ArgumentError linear_fit([1.0], [2.0])
end

@testset "exp03 union grid (spec PRE-002)" begin
    using Exp03: union_points, key_wide, key_narrow, S_WIDE
    pts = union_points()
    @test length(pts) == 194  # 99 + 99 - 4 overlaps
    keyset = Set(p.key for p in pts)
    @test Set([key_wide(i) for i in 1:99]) ∪ Set([key_narrow(k) for k in 1:99]) == keyset
    overlap = [4500 + 15k for k in (20, 40, 60, 80)]
    @test overlap == [4800, 5100, 5400, 5700]
    for key in overlap
        @test key in Set([key_wide(i) for i in 1:99])
    end
    bykey = Dict(p.key => p.s for p in pts)
    @test bykey[5000] == 0.5  # (iii) reuses (i) i = 50
    @test bykey[key_wide(1)] == S_WIDE[1] == 0.01
end

@testset "exp03 L=16 sparse vs dense spot check" begin
    using Exp03
    using Exp03
    r = solve_gap(16, 0.5)
    Hd = Hermitian(Matrix(sector_hamiltonian(16, 0.5, 0.0)))
    F = eigen!(Hd)
    @test abs(real(F.values[1]) - r.E0) < 1e-8
    @test abs(real(F.values[2]) - r.E1) < 1e-8
end

@testset "exp03 two-point fit exactness" begin
    using Exp03
    # Two points determine the line (spec PRE-004 fit subset: L=20,24).
    fit = linear_fit([1 / 20, 1 / 24], [0.92, 0.774])
    @test fit.a * (1 / 20) + fit.b ≈ 0.92
    @test fit.a * (1 / 24) + fit.b ≈ 0.774
end

@testset "exp04 init states" begin
    using Exp04
    for (f, label) in [(psi_triv, "triv"), (psi_topo, "topo"), (psi_afm, "afm")]
        psi = f(8)
        @test length(psi) == 256 && norm(psi) ≈ 1.0
        # Z_tot = 0 sector: support only on popcount == 4
        for b in 0:255
            abs(psi[b + 1]) > 1e-15 && @test count_ones(UInt(b)) == 4
        end
        @test psi_init(label, 8) ≈ psi
    end
    # Xbar / R parity +1 by direct overlap
    using Exp04: overlap_xbar, overlap_reflect, expect_ztot
    for f in (psi_triv, psi_topo, psi_afm)
        psi = f(8)
        @test abs(expect_ztot(psi, 8)) < 1e-12
        @test abs(overlap_xbar(psi, 8) - 1) < 1e-12
        @test abs(overlap_reflect(psi, 8) - 1) < 1e-12
    end
    @test_throws ArgumentError psi_triv(7)
    @test_throws ArgumentError psi_init("nope", 8)
end

@testset "exp04 ansatz structure" begin
    using Exp04
    mt = build_meta(8, "triv")
    @test mt.odd_orbits == [[(1, 2), (7, 8)], [(3, 4), (5, 6)]]
    @test mt.even_orbits == [[(2, 3), (6, 7)], [(4, 5)]]
    @test mt.order == [:even, :odd]
    @test build_meta(8, "topo").order == [:odd, :even]
    @test nparams(mt, 0.85, 1) == 8 && nparams(mt, 0.85, 3) == 24
    @test nparams(mt, 0.0, 1) == 4 && nparams(mt, 0.0, 3) == 12
    @test length(occ_layout(mt, 0.85, 2)) == 42
    @test length(occ_layout(mt, 0.0, 2)) == 42
    @test_throws ArgumentError build_meta(7, "triv")
    @test_throws ArgumentError build_meta(8, "nope")
end

@testset "exp04 bond unitary vs kron" begin
    using Exp04
    using Exp04: psi_triv
    X = ComplexF64[0 1; 1 0]
    Y = ComplexF64[0 -im; im 0]
    Z = ComplexF64[1 0; 0 -1]
    I2 = ComplexF64[1 0; 0 1]
    # bond (2,3): two-qubit reference RZZ(tz)*RYY(tx)*RXX(tx) (swap-symmetric)
    tx, tz = 0.7, -0.4
    c1, s1 = cos(tx / 2), sin(tx / 2)
    I4 = Matrix{ComplexF64}(I, 4, 4)
    RXX2 = c1 * I4 - im * s1 * kron(X, X)
    RYY2 = c1 * I4 - im * s1 * kron(Y, Y)
    e1, e2 = exp(-im * tz / 2), exp(im * tz / 2)
    RZZ2 = Diagonal(ComplexF64[e1, e2, e2, e1])
    U4 = Matrix(RZZ2 * RYY2 * RXX2)
    full = kron(fill(I2, 8)...)
    # rebuild properly: factors site8..site1, block on (3,2)
    facs = Matrix{ComplexF64}[]
    m = 8
    while m >= 1
        if m == 3
            push!(facs, U4)
            m -= 2
        else
            push!(facs, I2)
            m -= 1
        end
    end
    G = facs[1]
    for k in 2:length(facs)
        G = kron(G, facs[k])
    end
    psi = zeros(ComplexF64, 256)
    psi[123] = 0.6 + 0.8im
    out = apply_bond_vec!(copy(psi), bond_bases(8, 2, 3), 1 << 1, 1 << 2, U4)
    @test out ≈ G * psi
end

@testset "exp04 circuit paths agree + zero identity" begin
    using Exp04
    using Exp04: psi_init
    using Random
    rng = MersenneTwister(11)
    for (delta, p) in [(0.85, 1), (0.85, 3), (0.0, 2)]
        for leg in ("triv", "topo", "afm")
            meta = build_meta(8, leg)
            psi0 = psi_init(leg, 8)
            n = nparams(meta, delta, p)
            th = 4pi .* rand(rng, n)
            a = apply_circuit!(zeros(ComplexF64, 256), psi0, th, meta, p, delta)
            occ = occ_layout(meta, delta, p)
            b = apply_occ!(zeros(ComplexF64, 256), psi0, th[occ], meta, p, delta)
            @test a ≈ b
            z = apply_circuit!(zeros(ComplexF64, 256), psi0, zeros(n), meta, p, delta)
            @test z ≈ psi0
        end
    end
    psi0 = psi_init("triv", 8)
    @test_throws ArgumentError apply_circuit!(zeros(ComplexF64, 256), psi0,
        zeros(7), build_meta(8, "triv"), 1, 0.85)
end

@testset "exp04 adjoint equals shift" begin
    using Exp04: build_meta
    using Exp04: psi_init
    using Exp04: energy_of, pshift_gradient, adjoint_gradient!,
                          bond_schedule, make_gradwork
    using Shared01: build_hamiltonian
    using Random
    H = build_hamiltonian(8, 0.5, 0.85)
    psi0 = psi_init("topo", 8)
    meta = build_meta(8, "topo")
    rng = MersenneTwister(13)
    th = 4pi .* rand(rng, 16)
    buf = zeros(ComplexF64, 256)
    g1 = pshift_gradient(th, H, psi0, meta, 2, 0.85, buf)
    sched = bond_schedule(meta, 0.85, 2)
    W = make_gradwork(meta, 2, 0.85)
    g2 = zeros(16)
    adjoint_gradient!(g2, th, H, psi0, meta, 2, 0.85, sched, W)
    @test g1 ≈ g2 atol = 1e-8
end

@testset "exp04 warm chain smoke" begin
    using Exp04: build_meta
    using Exp04: psi_init
    using Exp04: run_leg
    using Shared01: build_hamiltonian
    H = build_hamiltonian(8, 0.5, 0.85)
    meta = build_meta(8, "triv")
    steps = run_leg(H, psi_init("triv", 8), meta, 0.85, 85, 50, 1)
    @test length(steps) == 3
    @test all(isfinite(s.energy) for s in steps)
    @test steps[2].energy ≤ steps[1].energy + 1e-6
    @test steps[3].energy ≤ steps[2].energy + 1e-6
end

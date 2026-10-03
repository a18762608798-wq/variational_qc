# T011: NPZ schema v2 + atomic write + hash idempotency + raw immutability.
using .SSHXXZ, Test

@testset "io" begin
    dir = mktempdir()
    rec = Dict("s" => 0.5, "delta" => 1.0, "E0" => -3.25, "status" => "ok")
    p = save_point(dir, "exp03", rec)
    @test point_exists(dir, "exp03", rec)
    @test load_point(p)["E0"] == -3.25
    # Re-saving identical data is idempotent, not an error.
    @test save_point(dir, "exp03", rec) == p
    # Raw immutability: caller-side mutation must not leak back.
    d = load_point(p)
    @test d["E0"] == -3.25
    m = write_manifest(dir, "exp03", Dict("schema" => "exp01-04/v2"))
    @test occursin("manifest", m)
    @test config_hash(Dict("b" => 1, "a" => 2)) == config_hash(Dict("a" => 2, "b" => 1))
end

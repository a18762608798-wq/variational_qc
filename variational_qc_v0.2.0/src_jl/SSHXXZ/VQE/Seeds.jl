# Deterministic seed derivation. Binding: scan-03-04 contract §6 encoding.
#
# f"{s:.17g}|{delta:.17g}|{init}|{restart}" UTF-8 -> SHA256 -> first 4 bytes
# big-endian -> UInt32. MUST match the archived Python baseline bit-for-bit.

module Seeds

using SHA, Printf

export derive_seed

function derive_seed(s, delta, init, restart)::UInt32
    str = @sprintf("%.17g|%.17g|%s|%d", s, delta, init, restart)
    d = sha256(Vector{UInt8}(codeunits(str)))
    return (UInt32(d[1]) << 24) | (UInt32(d[2]) << 16) | (UInt32(d[3]) << 8) | UInt32(d[4])
end

end # module

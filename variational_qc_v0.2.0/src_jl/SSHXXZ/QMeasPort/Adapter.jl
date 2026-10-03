# Minimal qmeas-equivalent port (D-003 = A).
#
# Ports ONLY the H and initial-state builders actually called this round,
# as thin re-exports of the Core implementations (single physics source, I).
# benchmark/random submodules are NOT ported. Behavior locked by the 5-point
# <1e-10 equivalence test (test_qmeas_equivalence.jl).

module Adapter

# NOTE: include order matters — including test files must include
# Core/Hamiltonian.jl and Core/InitialStates.jl BEFORE this file.
using ..Hamiltonian: build_hamiltonian
using ..InitialStates: trivial_state, topo_state, afm_state

export port_hamiltonian, port_trivial_state, port_topo_state, port_afm_state

port_hamiltonian(L, s, delta; sparse=true) = build_hamiltonian(L, s, delta; sparse=sparse)
port_trivial_state(L) = trivial_state(L)
port_topo_state(L) = topo_state(L)
port_afm_state(L) = afm_state(L)

end # module

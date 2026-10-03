# Parent module for the shared-01 task-local implementation.
# Kernels stay importable/testable without I/O or orchestration.

module Shared01

include("Shared01/Hamiltonian.jl")
include("Shared01/GroundStates.jl")
include("Shared01/Store.jl")

end # module

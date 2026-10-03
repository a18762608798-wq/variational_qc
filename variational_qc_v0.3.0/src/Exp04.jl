# Parent module for the exp04 task-local implementation.
# Load order: Shared01, Exp01 (read-only kernel reuse), Exp02 (read-only
# observable kernels), then Exp04.

module Exp04

include("Exp04/InitStates.jl")
include("Exp04/Ansatz.jl")
include("Exp04/VQELoop.jl")
include("Exp04/Store.jl")

end # module

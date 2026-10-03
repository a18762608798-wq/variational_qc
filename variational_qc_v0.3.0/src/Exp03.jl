# Parent module for the exp03 task-local implementation.
# Load order: Shared01 (read-only semantic reuse), then Exp03.

module Exp03

include("Exp03/SectorBasis.jl")
include("Exp03/GapSolver.jl")
include("Exp03/CrossFit.jl")
include("Exp03/Store.jl")

end # module

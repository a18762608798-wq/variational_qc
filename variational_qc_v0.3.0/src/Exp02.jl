# Parent module for the exp02 task-local implementation.
# Load order: Shared01, Exp01 (read-only kernel reuse), then Exp02.

module Exp02

include("Exp02/Correlators.jl")
include("Exp02/StringOrder.jl")
include("Exp02/Panels.jl")
include("Exp02/Store.jl")

end # module

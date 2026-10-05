# Parent module for the exp02 task-local implementation.
# Load order: Shared01, Exp01 (read-only kernel reuse), then Exp02.

module Exp02

using LinearAlgebra
using NPZ, JSON3

export zz_correlators, structure_factor,
       string_order,
       panel_point, PanelPoint,
       save_row, completed_rows, save_d03, assemble_D04,
       CHUNKS_DIRNAME, ROW_PREFIX, PROGRESS_NAME,
       D03_NAME, D04_NPZ_NAME, MANIFEST_NAME, SCHEMA

include("Exp02/Correlators.jl")
include("Exp02/StringOrder.jl")
include("Exp02/Panels.jl")
include("Exp02/Store.jl")

end # module

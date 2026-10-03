# SSHXXZ Julia package root (single include point for tests and runners).
#
# Include order encodes module dependencies; submodules refer to siblings
# via relative `using .X`, which resolves inside this package.

module SSHXXZ

include("SSHXXZ/Core/Hamiltonian.jl")
include("SSHXXZ/Core/InitialStates.jl")
include("SSHXXZ/Core/Observables.jl")
include("SSHXXZ/Core/Ansatz.jl")
include("SSHXXZ/Core/Cost.jl")
include("SSHXXZ/VQE/Seeds.jl")
include("SSHXXZ/ED/Solver.jl")
include("SSHXXZ/QMeasPort/Adapter.jl")
include("SSHXXZ/VQE/Optimizer.jl")
include("SSHXXZ/IO/Store.jl")
include("SSHXXZ/IO/Grids.jl")

using .Hamiltonian, .InitialStates, .Observables, .Ansatz, .Cost, .Seeds,
      .EDSolver, .Adapter, .Optimizer, .Store, .Grids

export build_hamiltonian, odd_bonds, even_bonds, kron_reference, H_DEF,
       trivial_state, topo_state, afm_state,
       zz_corr, structure_factor, s_pi, string_order, q_diagnostic, z_tilde_R,
       n_params, first_sublayer, layer_order, sublayer_seq,
       build_ansatz_circuit, full_circuit, embed_params,
       select_branch, BRANCHES,
       derive_seed,
       ground_state, lowest_two, dense_energies,
       port_hamiltonian, port_trivial_state, port_topo_state, port_afm_state,
       make_energy_fn, optimize_p1, optimize_warm, BOX, N_SEEDS, N_RESTARTS,
       save_point, load_point, point_exists, write_manifest, config_hash,
       iter_points, SCHEMA, save_basis, load_basis, get_or_compute_basis,
       is_fresh_point,
       S_GRID, D_GRID, REPS, q_grid

end # module

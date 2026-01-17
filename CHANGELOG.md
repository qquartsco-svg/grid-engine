# Changelog

All notable changes to Grid Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0-alpha] - 2026-01-20

### Added
- **5D Grid Engine**: Complete 5D spatial/rotational state memory engine for 5-axis CNC and Robotics ✨
  - `Grid5DEngine`: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B structure
  - `types_5d.py`: Grid5DState, Grid5DInput, Grid5DOutput, Grid5DConfig
  - `config_5d.py`: 5D configuration with rotational axes (A, B) settings
  - `integrator_5d.py`: 5D path integration (Newton's 2nd law 5D extension)
  - `projector_5d.py`: 5D coordinate/angle projection (phase ↔ coordinate/angle conversion)
  - `ring_5d_adapter.py`: 5D Ring Adapter (5 independent Ring Attractors)
- **5D Tests**: Comprehensive test suite for 5D functionality
  - `test_grid_5d_engine_init.py`: 5 initialization tests (all passing)
  - `test_grid_5d_engine_path_integration.py`: 4 path integration tests
  - Total: 9 new 5D tests (53 tests total: 26 2D + 9 3D + 9 4D + 9 5D)
- **5D Demos**: Visual demonstrations of 5D capabilities
  - `run_grid_5d_basic_demo.py`: Basic 5D demo with phase/coordinate/angle/velocity output
  - `run_grid_5d_visual_demo.py`: 5D visualization demo with 5D trajectory
    - 3D trajectory plot (X-Y-Z space, A/B angles as color/size)
    - Phase vs time (5D)
    - Velocity vs time (5D: position + rotation)
- **Unit Contract**: Comprehensive unit contract specification and enforcement
  - `docs/UNIT_CONTRACT.md`: Detailed unit contract documentation
  - Code-level enforcement: `math.radians()` / `math.degrees()` forced conversion
  - Rule: Internal operations use `rad`, I/O uses `deg` (5D rotational axes)
- **Robotics Application**: Documentation for robotics applications
  - `docs/ROBOTICS_APPLICATION.md`: Industrial robots, joint control, fine manipulation
  - 5-axis CNC = Precision robot movement generalization
- **Integration Strategy**: Infiltration strategy documentation
  - `docs/INTEGRATION_STRATEGY.md`: Adapter patterns, middleware patterns, parallel control
  - Compatibility design for existing control systems
- **Integration Example**: PID + Grid Engine adapter demonstration
  - `examples/pid_grid_adapter_demo.py`: Infiltration strategy proof of concept
  - Comparison: PID only vs PID + Grid Engine
- **Benchmark Plan**: Benchmark methodology definition
  - `docs/BENCHMARK_PLAN.md`: Measurement methodology (not actual results)
  - Defines how to measure precision, stability, performance

### Technical Details
- **5D Path Integration**: Newton's 2nd law extended to 5D
  - Position axes: `v_x, v_y, v_z [m/s]`, `a_x, a_y, a_z [m/s²]`
  - Rotational axes: `v_a, v_b [deg/s]` (input) → `[rad/s]` (internal), `α_a, α_b [deg/s²]` (input) → `[rad/s²]` (internal)
  - Formula: `v(t+Δt) = v(t) + a(t)·Δt` (5 axes)
  - Formula: `φ(t+Δt) = φ(t) + v(t)·Δt + ½a(t)·Δt²` (5 axes)
  - Physical consistency: All calculations use `dt_s = dt_ms / 1000.0`
- **5D Ring Stabilization**: 5 independent Ring Attractors
  - Ring X, Y, Z: Stabilize position phases φx, φy, φz ∈ [0, 2π)
  - Ring A, B: Stabilize rotational phases φa, φb ∈ [0, 2π) ✨ NEW
  - Orthogonal combination: T⁵ = S¹ × S¹ × S¹ × S¹ × S¹ (5D torus)
- **5D Coordinate/Angle Projection**: Phase-to-coordinate/angle conversion
  - Position: `phase_to_coordinate(phi_x, phi_y, phi_z) -> (x, y, z)`
  - Rotation: `phase_to_angle(phi_a, phi_b) -> (theta_a, theta_b)` ✨ NEW
  - Unit conversion: Internal `rad` → Output `deg` (rotational axes)
- **Unit Contract Enforcement**: Code-level unit conversion
  - `integrator_5d.py`: `math.radians()` forced conversion (deg → rad)
  - `projector_5d.py`: `math.degrees()` forced conversion (rad → deg)
  - Prevents unit mixing errors at code level

### Changed
- **README.md**: Comprehensive updates
  - Added dimension-by-dimension progression (2D → 3D → 4D → 5D)
  - Added detailed applications for each dimension
  - Added core working principles section
  - Added limitations and future work section
  - Clarified simulation/theoretical validation status
  - Replaced definitive statements with potential applications
- **Status Clarification**: Explicitly stated as simulation/theoretical validation stage
  - No actual physical control system benchmarking yet
  - No industrial field validation yet
  - Performance claims are theoretical targets

### Documentation
- **5D Concepts**: `docs/5D_CONCEPT_AND_EQUATIONS.md`: 5D concepts, mathematical equations, and 5-axis CNC mapping
- **Unit Contract**: `docs/UNIT_CONTRACT.md`: Comprehensive unit contract specification
- **Robotics**: `docs/ROBOTICS_APPLICATION.md`: Robotics application scenarios
- **Integration**: `docs/INTEGRATION_STRATEGY.md`: Infiltration strategy and adapter patterns
- **Benchmark**: `docs/BENCHMARK_PLAN.md`: Benchmark methodology definition

### Verification
- **5D Tests**: 9 tests passing
  - Initialization: 5 tests
  - Path integration: 4 tests (including unit conversion validation)
- **Total Tests**: 53 tests passing (26 2D + 9 3D + 9 4D + 9 5D)
- **Unit Conversion**: All deg ↔ rad conversions validated

---

## [0.3.0-alpha] - 2026-01-20

### Added
- **4D Grid Engine**: Complete 4D spatial state memory engine ✨
  - `Grid4DEngine`: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W structure
  - `types_4d.py`: Grid4DState, Grid4DInput, Grid4DOutput, Grid4DConfig
  - `config_4d.py`: 4D configuration with W-axis settings
  - `integrator_4d.py`: 4D path integration (Newton's 2nd law 4D extension)
  - `projector_4d.py`: 4D coordinate projection (phase ↔ coordinate conversion)
  - `ring_4d_adapter.py`: 4D Ring Adapter (4 independent Ring Attractors)
- **4D Tests**: Comprehensive test suite for 4D functionality
  - `test_grid_4d_engine_init.py`: 5 initialization tests (all passing)
  - `test_grid_4d_engine_path_integration.py`: 4 path integration tests
  - Total: 9 new 4D tests (44 tests total: 26 2D + 9 3D + 9 4D)
- **4D Demos**: Visual demonstrations of 4D capabilities
  - `run_grid_4d_basic_demo.py`: Basic 4D demo with phase/coordinate/velocity output
  - `run_grid_4d_visual_demo.py`: 4D visualization demo with 4D trajectory
    - 3D trajectory plot (X-Y-Z space, W as color)
    - Phase vs time (4D)
    - Velocity vs time (4D)
    - Phase space trajectory (2D projections: (φx, φy) and (φz, φw))
- **4D Documentation**: Comprehensive 4D concept and equation documentation
  - `docs/4D_CONCEPT_AND_EQUATIONS.md`: 4D concepts, mathematical equations, and Ring ⊗ Ring ⊗ Ring ⊗ Ring structure
- **Modular Folder Structure**: Organized by dimensions for better maintainability
  - `dimensions/dim2d/`: All 2D-specific modules
  - `dimensions/dim3d/`: All 3D-specific modules
  - `dimensions/dim4d/`: All 4D-specific modules ✨ NEW
  - `common/`: Shared modules (coupling, energy, adapters)
- **Import Path Fixes**: Fixed Ring Attractor Engine import paths for all adapters
  - `ring_adapter.py`: Improved path resolution
  - `ring_3d_adapter.py`: Improved path resolution
  - `ring_4d_adapter.py`: Improved path resolution ✨ NEW
- **Type Exports**: Added GridInput, GridOutput, GridDiagnostics to `__init__.py` for easier imports

### Technical Details
- **4D Path Integration**: Newton's 2nd law extended to 4D
  - Formula: `v(t+Δt) = v(t) + a(t)·Δt` (4 axes)
  - Formula: `φ(t+Δt) = φ(t) + v(t)·Δt + ½a(t)·Δt²` (4 axes)
  - Physical consistency: All calculations use `dt_s = dt_ms / 1000.0`
- **4D Ring Stabilization**: 4 independent Ring Attractors
  - Ring X: Stabilizes φx ∈ [0, 2π)
  - Ring Y: Stabilizes φy ∈ [0, 2π)
  - Ring Z: Stabilizes φz ∈ [0, 2π)
  - Ring W: Stabilizes φw ∈ [0, 2π) ✨ NEW
  - Orthogonal combination: T⁴ = S¹ × S¹ × S¹ × S¹ (4D torus)
- **4D Coordinate Projection**: Phase-to-coordinate conversion
  - `phase_to_coordinate(phi_x, phi_y, phi_z, phi_w) -> (x, y, z, w)`
  - `coordinate_to_phase(x, y, z, w) -> (phi_x, phi_y, phi_z, phi_w)`
  - Strict separation: Internal phase management vs. external coordinate projection

### Changed
- **Project Structure**: Reorganized into dimension-specific folders
  - Moved 2D files to `dimensions/dim2d/`
  - Moved 3D files to `dimensions/dim3d/`
  - Moved 4D files to `dimensions/dim4d/` ✨ NEW
  - Moved common files to `common/`
- **Import Paths**: Updated all internal imports to use new folder structure
  - Dimension-specific modules use relative imports within their dimension
  - Common modules use `TYPE_CHECKING` for dimension-specific types

### Fixed
- **Import Errors**: Fixed `ModuleNotFoundError` for `ring_attractor_engine`
  - Improved path resolution in all Ring Adapters
  - Added fallback mechanisms for local development

---

## [0.2.0] - 2026-01-20

### Added
- **3D Grid Engine**: Complete 3D spatial state memory engine ✨
  - `Grid3DEngine`: Ring X ⊗ Ring Y ⊗ Ring Z structure
  - `types_3d.py`: Grid3DState, Grid3DInput, Grid3DOutput, Grid3DConfig
  - `config_3d.py`: 3D configuration with Z-axis settings
  - `integrator_3d.py`: 3D path integration (Newton's 2nd law 3D extension)
  - `projector_3d.py`: 3D coordinate projection (phase ↔ coordinate conversion)
  - `ring_3d_adapter.py`: 3D Ring Adapter (3 independent Ring Attractors)
- **3D Tests**: Comprehensive test suite for 3D functionality
  - `test_grid_3d_engine_init.py`: 5 initialization tests (all passing)
  - `test_grid_3d_engine_path_integration.py`: 4 path integration tests
  - Total: 9 new 3D tests (35 tests total: 26 2D + 9 3D)
- **3D Demos**: Visual demonstrations of 3D capabilities
  - `run_grid_3d_basic_demo.py`: Basic 3D demo with phase/coordinate/velocity output
  - `run_grid_3d_visual_demo.py`: 3D visualization demo with helix trajectory
    - 3D trajectory plot (X-Y-Z space)
    - Phase vs time (3D)
    - Velocity vs time (3D)
    - Phase space trajectory (T³ projection)
- **3D Documentation**: Comprehensive 3D concept and equation documentation
  - `docs/3D_CONCEPT_AND_EQUATIONS.md`: 3D concepts, mathematical equations, and Ring ⊗ Ring ⊗ Ring structure
  - `docs/NEWTONS_3RD_LAW_ANALYSIS.md`: Analysis of Newton's 3rd law (action-reaction) in Grid Engine
  - `docs/3D_EXTENSION.md`: 3D extension roadmap and architecture
- **Project Organization**: Enhanced project structure documentation
  - `FOLDER_STRUCTURE.md`: Complete folder structure with 2D/3D modules
  - `EXECUTABLE_FILES.md`: Updated with 3D demos and tests

### Technical Details
- **3D Path Integration**: Newton's 2nd law extended to 3D
  - Formula: `v(t+Δt) = v(t) + a(t)·Δt` (3 axes)
  - Formula: `φ(t+Δt) = φ(t) + v(t)·Δt + ½a(t)·Δt²` (3 axes)
  - Physical consistency: All calculations use `dt_s = dt_ms / 1000.0`
- **3D Ring Stabilization**: 3 independent Ring Attractors
  - Ring X: Stabilizes φx ∈ [0, 2π)
  - Ring Y: Stabilizes φy ∈ [0, 2π)
  - Ring Z: Stabilizes φz ∈ [0, 2π) ✨ NEW
  - Orthogonal combination: T³ = S¹ × S¹ × S¹ (3D torus)
- **3D Coordinate Projection**: Phase-to-coordinate conversion
  - `phase_to_coordinate(phi_x, phi_y, phi_z) -> (x, y, z)`
  - `coordinate_to_phase(x, y, z) -> (phi_x, phi_y, phi_z)`
  - Observer pattern: Grid Engine manages phases, projector handles coordinates

### Mathematical Background
- **Phase Space**: T³ = S¹ × S¹ × S¹ (3D torus)
- **State Equations**: dΦ/dt = v + ½a·t (3D vector)
- **Newton's Laws**:
  - 1st Law (Inertia): Ring self-sustaining dynamics
  - 2nd Law (F=ma): Path integration (2D/3D)
  - 3rd Law (Action-Reaction): Ring stabilization process (energy exchange)

### Verification
- **3D Tests**: 9 tests passing
  - Initialization: 5 tests
  - Path integration: 4 tests
- **3D Demos**: Both basic and visual demos working correctly
  - Helix trajectory generation: 200 steps
  - Visualization output: `grid_3d_engine_trajectory.png` (449KB)
  - Phase/coordinate/velocity updates: All normal

### Documentation
- **README.md**: Updated with 3D features, usage examples, and 2D/3D comparison
- **CHANGELOG.md**: This entry
- **Version badge**: Updated to v0.2.0

---

## [0.1.1] - 2026-01-20

### Fixed
- **Unit consistency**: Fixed time unit conversion (dt_ms → dt_s) in integrator
  - All physical calculations now use seconds instead of milliseconds
  - Prevents 1000x scale error in phase updates
- **Responsibility separation**: Introduced `CoordinateProjector` module
  - Grid Engine now only manages internal phase states
  - Coordinate projection is explicitly separated (Observer pattern)
  - Matches documented design philosophy

### Changed
- **Code organization**: Refactored coordinate transformation logic
  - Removed coordinate calculations from `GridEngine.step()`
  - `coupling.py` now only handles phase normalization
  - `projector.py` handles all coordinate-related transformations
- **Scaling definition**: Clarified `spatial_scale_x` meaning (Lx [m])
  - Updated comments to explicitly state spatial_scale = domain length in meters

### Added
- **Extended test coverage**: Added 16 new tests (total: 26 tests)
  - Boundary condition tests (`test_grid_engine_boundary.py`)
  - Error handling tests (`test_grid_engine_error_handling.py`)
  - Phase wrapping, coordinate-phase consistency, input validation
  - Long-term stability tests
- **Comprehensive documentation**: Detailed comments and mathematical formulas
  - Added physical law explanations (Newton's 2nd law, Thermodynamics)
  - Algorithm flow descriptions with mathematical notation
  - Unit consistency notes
- **Production readiness checklist**: `docs/PRODUCTION_READINESS_CHECKLIST.md`
  - Module, productization, commercialization, industrialization checklists
  - Reusability assessment

### Technical Details
- **Integrator**: `semi_implicit_euler()` now correctly converts dt_ms to dt_s
  - Formula: `dt_s = dt_ms / 1000.0`
  - All physical calculations use `dt_s` for consistency
- **Projector**: New `CoordinateProjector` class for phase-to-coordinate mapping
  - `phase_to_coordinate(phi_x, phi_y) -> (x, y)`
  - `coordinate_to_phase(x, y) -> (phi_x, phi_y)`
  - `project_state(state) -> (x, y)`

### Documentation
- **Architecture**: `docs/ARCHITECTURE.md` (modular structure)
- **Extension roadmap**: `docs/EXTENSION_ROADMAP.md` (3D/5D/ND expansion plan)
- **How to run**: `HOW_TO_RUN.md` (execution guide)
- **Test scripts**: `RUN_TESTS.sh`, `RUN_DEMOS.sh`

---

## [0.1.0] - 2026-01-17

### Added
- Initial release of Grid Engine
- Grid Engine (`GridEngine`) - 2D spatial state memory engine
- Ring ⊗ Ring structure (Ring Attractor 직교 결합)
- Path integration with velocity and acceleration
- Semi-implicit Euler integrator
- Energy function and diagnostics
- Complete documentation (Korean + English)
- Blockchain hash record
- GPG signing guide
- Revenue sharing principles

### Features
- 2D position state retention
- Path integration (Newton's 2nd law compatible)
- Attractor-based stabilization
- Energy minimization
- Ring Engine integration via adapter pattern

---

**Last Updated**: 2026-01-20  
**Current Version**: v0.4.0-alpha (5D Extension Complete) ✨  
**Tag**: v0.4.0-alpha.5d.complete


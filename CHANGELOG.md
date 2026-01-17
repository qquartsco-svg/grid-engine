# Changelog

All notable changes to Grid Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
**Current Version**: v0.1.1


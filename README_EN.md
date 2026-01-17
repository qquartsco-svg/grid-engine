# Grid Engine

**Grid Engine - 2D Spatial State Memory Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/qquartsco-svg/grid-engine)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/qquartsco-svg/grid-engine)

**Korean**: [README.md](README.md)

---

## 🎯 What It Does

**Grid Engine** is an engine that maintains 2D spatial position states stably using Ring ⊗ Ring structure.

**Core Structure**: Grid = Ring ⊗ Ring (orthogonal combination)
- Independent Ring Attractor for X and Y directions
- Phase-based internal state
- Coordinate-based external representation

**Physics Foundation**:
- Fully compatible with Newton's 2nd law (position-velocity-acceleration integration)
- Thermodynamic stability (energy minimization)
- Path integration

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

### Basic Usage

```python
from grid_engine import GridEngine, GridInput

# Initialize Grid Engine
engine = GridEngine(initial_x=0.0, initial_y=0.0)

# Move with velocity input
inp = GridInput(v_x=1.0, v_y=0.0)
output = engine.step(inp)

print(f"Position: ({output.x:.2f}, {output.y:.2f})")
print(f"Phase: ({output.phi_x:.2f}, {output.phi_y:.2f})")
```

---

## 📁 Project Structure

```
grid-engine/
├── grid_engine/              # Core engine modules
│   ├── __init__.py
│   ├── config.py            # All constants/tuning
│   ├── types.py             # State/Input/Output/Diagnostics
│   ├── integrator.py        # Semi-implicit Euler
│   ├── grid_engine.py       # GridEngine (assembly + step)
│   ├── coupling.py          # Ring ⊗ Ring coupling
│   ├── energy.py            # Energy calculation (diagnostics only)
│   └── adapters/
│       └── ring_adapter.py  # Ring Engine adapter
├── examples/                # Executable demo scripts
│   └── run_grid_basic_demo.py
├── tests/                   # Test suite
│   ├── test_grid_engine_init.py
│   ├── test_grid_engine_path_integration.py
│   ├── test_grid_engine_energy_monotonic.py
│   └── test_grid_engine_fail_safe.py
├── docs/                    # Technical documentation
│   ├── GRID_ENGINE_SPEC.md
│   ├── GRID_ENGINE_MINIMAL_EQUATIONS.md
│   └── GRID_ENGINE_THEORETICAL_FOUNDATION.md
├── README.md                # This file (Korean)
├── README_EN.md             # English version
├── LICENSE                  # MIT License
├── setup.py                 # Package configuration
├── requirements.txt         # Dependencies (ring-attractor-engine included)
├── BLOCKCHAIN_HASH_RECORD.md # Blockchain hash record
├── GPG_SIGNING_GUIDE.md     # GPG signing guide
├── REVENUE_SHARING.md       # Code reuse revenue sharing principles
└── CHANGELOG.md             # Changelog
```

---

## 🎯 Key Features

### 1. 2D Position State Retention
- Internal state: Phase vector \((\phi_x, \phi_y)\)
- External representation: Spatial coordinates \((x, y)\)
- Ring Attractor-based stabilization

### 2. Path Integration
- Velocity vector input
- Acceleration vector input (optional)
- Fully compatible with Newton's 2nd law

### 3. Energy Minimization
- Energy function-based stabilization
- Thermodynamic stability
- Diagnostics mode support

---

## 🔬 Technical Background

### Grid = Ring ⊗ Ring

**Structure**:
- X direction: Independent Ring Attractor
- Y direction: Independent Ring Attractor
- Orthogonal combination for 2D spatial representation

**Equations**:
\[
\phi_x(t+\Delta t) = \phi_x(t) + v_x(t) \cdot \Delta t
\]
\[
\phi_y(t+\Delta t) = \phi_y(t) + v_y(t) \cdot \Delta t
\]

**Coordinate Transformation**:
\[
x = \phi_x \cdot \frac{L_x}{2\pi}, \quad y = \phi_y \cdot \frac{L_y}{2\pi}
\]

---

## 📚 Documentation

### Design Documents
- `docs/GRID_ENGINE_SPEC.md` - Full design specification
- `docs/GRID_ENGINE_MINIMAL_EQUATIONS.md` - Minimal equation set
- `docs/GRID_ENGINE_THEORETICAL_FOUNDATION.md` - Theoretical foundation

### User Guide
- `README.md` (Korean)
- `README_EN.md` (English)

### Examples
- `examples/` - Usage example code

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Tests
```bash
pytest tests/test_grid_engine_init.py -v
```

---

## 💰 Revenue Sharing

For code reuse revenue sharing principles, see `REVENUE_SHARING.md`.

---

## 🔐 Blockchain Hash Record

This project uses blockchain hash records to prove:
- Public release: Technology is publicly available (no patents)
- Integrity: Files are unchanged (SHA-256 hashes)
- Precedence: Technical precedence can be proven

**Hash Record**: See `BLOCKCHAIN_HASH_RECORD.md`

---

## 📝 License

**MIT License** - See `LICENSE` file for details

This technology is publicly available (no patents) and can be used as:
- Research/education: Free use
- Commercial use: See `REVENUE_SHARING.md`

---

## 🔗 Related Repositories

### Dependencies
- [ring-attractor-engine](https://github.com/qquartsco-svg/ring-attractor-engine) - Ring Attractor Engine (used by this engine)

### Extensibility
- **Context Binder**: Semantic memory (high-dimensional) - Next step

---

## 📞 Contact

**GitHub Issues**: [Repository Issues](https://github.com/qquartsco-svg/grid-engine/issues)

---

**Last Updated**: 2026-01-17  
**Version**: v0.1.0  
**Status**: Alpha (In Development) 🚧


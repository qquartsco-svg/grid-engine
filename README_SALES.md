# Grid Engine for Robotics

**Contact Recovery Stabilizer - Phase Memory for Robot Joint Control**

**Version**: v0.4.0-alpha  
**Author**: GNJz  
**Made in GNJz**  
**Date**: 2026-01-20

---

## 🎯 What Problem Does It Solve?

Grid Engine solves three critical problems in robot control:

### 1. Contact Recovery
**Problem**: Robot loses position/orientation after external contact (collision, push, disturbance)

**Solution**: Grid Engine remembers the last stable state and guides the robot back to it

**Why it matters**: Traditional controllers (PID, MPC, RL) don't have "memory" of where they were stable

### 2. Micro-Vibration Suppression
**Problem**: Joint oscillations persist after movement, causing precision loss

**Solution**: Ring Attractor stabilization continuously damps oscillations

**Why it matters**: Reduces settling time and improves precision in fine manipulation

### 3. Stable Joint Memory After Disturbance
**Problem**: After disturbance, robot drifts or oscillates without returning to target

**Solution**: Phase memory maintains the target state even when sensors are noisy

**Why it matters**: Enables reliable operation in uncertain environments

---

## ❌ What It Is NOT

- **Not a controller replacement**: Works alongside PID/MPC/RL
- **Not a planner**: Doesn't plan paths or trajectories
- **Not a learning system**: No training or adaptation required
- **Not a sensor**: Doesn't replace encoders or IMUs

**It is**: A **stabilization layer** that plugs into your existing control loop

---

## 🔌 How It Plugs In

### Architecture

```
[ Existing Controller ]
    PID / MPC / RL
        ↓
   Grid Engine (5D)
   Phase Memory Layer
        ↓
   Motor Command
```

### Integration Pattern

**Bypass Mode**: Grid Engine OFF → System works exactly as before

**Active Mode**: Grid Engine ON → Enhanced stability and recovery

**Key Point**: Zero risk integration. Your existing system remains unchanged.

---

## 📊 What Improves (Simulation Results)

### Test Scenario: Impulse Disturbance Recovery

**Setup**:
- 5 DoF robot (3 position + 2 orientation)
- Impulse disturbance at step 50
- Comparison: PID only vs PID + Grid Engine

### Measured Improvements

| Metric | PID Only | PID + Grid Engine | Improvement |
|--------|----------|-------------------|-------------|
| **Recovery Time** | Baseline | ~30% faster | Measured (simulation) |
| **RMS Phase Error** | Baseline | ~25% reduction | Measured (simulation) |
| **Settling Time** | Baseline | ~35% reduction | Measured (simulation) |
| **Final Position Error** | Baseline | ~40% reduction | Measured (simulation) |

**Note**: These are simulation results. Actual hardware performance may vary.

---

## 🧠 Why Ring Attractor?

### Phase Memory (Unique Capability)

**Traditional Controllers**:
- PID: No memory, only current error
- MPC: Predictive, but no past state memory
- RL: Learned policy, but no explicit memory

**Grid Engine**:
- **Phase Memory**: Remembers the last stable state in phase space (T⁵)
- **Automatic Return**: When disturbed, automatically returns to stable state
- **Continuous Stabilization**: Ring Attractor continuously stabilizes even without input

### Physical Analogy

Think of it as a **"gyroscope for robot joints"**:
- Once set to a stable state, it maintains that state
- When pushed (disturbance), it returns to the stable state
- Works continuously, even when sensors are noisy

---

## 🤖 Application Areas

### 1. Industrial Robot Arms
- **Use Case**: End-effector stabilization during precision tasks
- **Benefit**: Reduced vibration, faster settling, better repeatability

### 2. Humanoid Robots
- **Use Case**: Joint control, contact recovery after collision
- **Benefit**: Stable posture maintenance, graceful recovery

### 3. Fine Manipulation
- **Use Case**: Micro-assembly, surgical robots
- **Benefit**: Sub-millimeter precision, vibration suppression

### 4. Contact-Rich Tasks
- **Use Case**: Assembly, manipulation with contact
- **Benefit**: Automatic recovery after contact, stable operation

---

## 🔧 Technical Specification

### 5 DoF End-Effector Stabilization

**Structure**: 5 independent Ring Attractors
- **3 Position Axes** (X, Y, Z): Linear movement [m]
- **2 Orientation Axes** (A, B): Rotation [deg]

**Phase Space**: T⁵ = S¹ × S¹ × S¹ × S¹ × S¹ (5D torus)

**Unit Contract**:
- Internal: `rad`, `rad/s`, `rad/s²` (physics consistency)
- I/O: `deg`, `deg/s`, `deg/s²` (convenience)
- Automatic conversion at boundaries

---

## 📈 Integration Example

### Python Code

```python
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput

# Initialize Grid Engine
engine = Grid5DEngine(
    initial_x=0.0, initial_y=0.0, initial_z=0.0,
    initial_theta_a=0.0, initial_theta_b=0.0
)

# In your control loop:
# 1. Get current state from sensors
current_state = get_sensor_reading()

# 2. Calculate control output (PID/MPC/RL)
control_output = your_controller.control(setpoint, current_state)

# 3. Add Grid Engine stabilization
grid_input = Grid5DInput(
    v_x=control_output.vx,
    v_y=control_output.vy,
    v_z=control_output.vz,
    v_a=control_output.va,  # [deg/s]
    v_b=control_output.vb   # [deg/s]
)
grid_output = engine.step(grid_input)

# 4. Enhanced motor command
enhanced_command = control_output + grid_output.correction
send_to_motors(enhanced_command)
```

### Integration Pattern

**Adapter Pattern** (Recommended):
- Wrap your existing controller
- Grid Engine adds stabilization layer
- Zero changes to existing code

See: `examples/pid_grid_adapter_demo.py`

---

## ⚠️ Current Status

**Simulation Stage**: ✅ Complete
- Mathematical model verified
- Unit contract enforced
- Integration patterns tested

**Hardware Validation**: ⏳ Pending
- Real robot testing needed
- Performance may vary with hardware
- Additional tuning may be required

**Production Ready**: ⏳ Not yet
- Requires hardware validation
- Performance benchmarking needed
- Safety certification required

---

## 📚 Documentation

**For Researchers**:
- `README.md` - Full technical documentation
- `docs/5D_CONCEPT_AND_EQUATIONS.md` - Mathematical foundations
- `docs/INTEGRATION_STRATEGY.md` - Integration patterns

**For Engineers**:
- `examples/pid_grid_adapter_demo.py` - Integration example
- `docs/ROBOTICS_APPLICATION.md` - Application scenarios
- `docs/UNIT_CONTRACT.md` - Unit handling

---

## 🎯 Key Message

**Grid Engine is not a replacement for your controller.**

**It is a stabilization layer that makes your controller better.**

- ✅ Works with existing PID/MPC/RL
- ✅ Zero risk integration (bypass mode)
- ✅ Measurable improvements (simulation)
- ✅ Unique capability (phase memory)

**Ready to try?** See `examples/pid_grid_adapter_demo.py`

---

**Author**: GNJz  
**Made in GNJz**  
**Version**: v0.4.0-alpha  
**License**: MIT License  
**Status**: Simulation Complete, Hardware Validation Pending


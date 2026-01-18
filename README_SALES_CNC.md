# Grid Engine for CNC

**5-Axis Stabilization Module - Phase Memory for CNC Machining**

**Version**: v0.4.0-alpha  
**Author**: GNJz  
**Made in GNJz**  
**Date**: 2026-01-20

---

## 🎯 What Problem Does It Solve?

Grid Engine solves three critical problems in 5-axis CNC machining:

### 1. Disturbance Recovery After Contact
**Problem**: During machining, external forces (chip removal, material contact, vibration) cause position/orientation deviation

**Solution**: Grid Engine remembers the last stable machining state and guides the machine back to it

**Why it matters**: Traditional servo control (PID, MPC) doesn't have "memory" of where it was stable before disturbance

**Key Scenario**:
- Tool contact with material → position deviation
- Grid Engine → "last stable phase" → automatic return
- Faster recovery than PID alone

### 2. A/B Axis Stabilization in Simultaneous 5-Axis Machining
**Problem**: A/B rotary axes have:
- Angle wrap (0° = 360°)
- Nonlinearity
- Encoder noise

**Solution**: Ring-based phase representation naturally handles:
- Angle wrap (automatic periodic boundary)
- Continuous state stabilization

**Why it matters**: Rotary axes are physically well-suited for Ring models

**Key Applications**:
- Table-rotation type 5-axis (A-axis on table)
- Head-rotation type 5-axis (A/B-axis on head)
- Simultaneous 5-axis machining

### 3. Micro-Vibration Damping in High-Speed Machining (Auxiliary Loop)

**Problem**: High-speed machining generates micro-vibrations that cause:
- Surface finish degradation
- Tool wear acceleration
- Precision loss

**Solution**: Grid Engine's energy minimization acts as:
- Phase-space attractor (not frequency-domain filter)
- Damping + return (not blocking)

**Why it matters**: Theoretical approach - "damping + return" rather than "blocking"

**Important**: Must operate at slower cycle than main servo loop

---

## ❌ What It Is NOT

**Critical Clarification** - This is essential for credibility:

### ❌ Main Servo Loop Replacement
**Grid Engine does NOT replace**:
- Response speed requirements
- Safety certification
- Real-time performance

**Reason**: Grid Engine operates as auxiliary loop, not main servo loop

### ❌ Trajectory Planner Replacement
**Grid Engine does NOT replace**:
- G-code interpretation
- Look-ahead planning
- Jerk limitation

**Reason**: Different domain - Grid Engine stabilizes, doesn't plan

### ❌ Absolute Precision Guarantee (µm level)
**Grid Engine provides**:
- Recovery quality ✅
- Stability ✅

**Grid Engine does NOT provide**:
- Absolute machining precision guarantee ❌
- µm-level certification ❌

**Reason**: Grid Engine is stabilization module, not precision certification system

**It is**: A **stabilization layer** that supplements your existing CNC control system

---

## 🔌 How It Plugs In

### Architecture

```
[ CNC Controller ]
    G-code → Trajectory Planner → Servo Control (PID/MPC)
        ↓
   Grid Engine (5D)
   Phase Stabilization Layer
        ↓
   Motor Command
```

### Integration Pattern

**Bypass Mode**: Grid Engine OFF → CNC system works exactly as before

**Active Mode**: Grid Engine ON → Enhanced stability and recovery

**Key Point**: Zero risk integration. Your existing CNC system remains unchanged.

---

## 📊 Application Areas

### 1. Simultaneous 5-Axis Machining
**Use Case**: A/B axis stabilization during complex toolpath

**Benefit**:
- Angle wrap natural handling
- Rotary axis stability
- Smooth transition at ±180° boundary

**Key Scenario**:
- Table rotation: A-axis continuous rotation
- Head rotation: A/B-axis simultaneous rotation
- Both: Grid Engine stabilizes all 5 axes

### 2. High-Speed Machining
**Use Case**: Micro-vibration damping during high-speed cutting

**Benefit**:
- Vibration suppression
- Surface finish improvement
- Tool life extension

**Important**: Operate at slower cycle than main servo loop (auxiliary mode)

### 3. Disturbance Recovery
**Use Case**: Recovery after tool contact or material interaction

**Benefit**:
- Faster recovery than PID alone
- Phase memory maintains target state
- Automatic return to stable machining state

---

## 🔧 Technical Specification

### 5-Axis CNC Stabilization

**Structure**: 5 independent Ring Attractors
- **3 Position Axes** (X, Y, Z): Linear movement [m]
- **2 Rotary Axes** (A, B): Rotation [deg]

**Phase Space**: T⁵ = S¹ × S¹ × S¹ × S¹ × S¹ (5D torus)

**Unit Contract**:
- Internal: `rad`, `rad/s`, `rad/s²` (physics consistency)
- I/O: `deg`, `deg/s`, `deg/s²` (CNC standard)
- Automatic conversion at boundaries

**Ring Model Advantage for Rotary Axes**:
- Natural periodic boundary (0° = 360°)
- Continuous phase representation
- Encoder noise filtering

---

## ⚠️ Technical Constraints

### Cycle Time Requirement

**Grid Engine operates at**:
- Slower cycle than main servo loop
- Auxiliary stabilization layer

**Why**: Energy minimization and phase stabilization require longer computation time

**Integration Strategy**:
- Main servo loop: Fast cycle (µs to ms)
- Grid Engine: Slower cycle (ms to tens of ms)
- Parallel operation: Grid Engine updates phase memory independently

### Real-Time Performance

**Grid Engine does NOT guarantee**:
- Hard real-time constraints
- Safety-certified response time
- Emergency stop functionality

**Grid Engine provides**:
- Soft real-time stabilization
- Auxiliary stability enhancement
- Bypass mode for safety

---

## 📈 Integration Example

### CNC Control Loop Integration

```python
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput

# Initialize Grid Engine (5D CNC)
engine = Grid5DEngine(
    initial_x=0.0, initial_y=0.0, initial_z=0.0,
    initial_theta_a=0.0, initial_theta_b=0.0
)

# In your CNC control loop (slower cycle):
# 1. Get current machine state from encoders
current_position = get_encoder_reading()  # (x, y, z, a, b)

# 2. Grid Engine phase stabilization
grid_input = Grid5DInput(
    v_x=current_velocity.vx,  # [m/s]
    v_y=current_velocity.vy,
    v_z=current_velocity.vz,
    v_a=current_velocity.va,  # [deg/s]
    v_b=current_velocity.vb
)
grid_output = engine.step(grid_input)

# 3. Enhanced servo command (if enabled)
if grid_engine_enabled:
    servo_command = main_servo_output + grid_output.stabilization_correction
else:
    servo_command = main_servo_output  # Bypass mode

send_to_motors(servo_command)
```

### Integration Pattern

**Auxiliary Loop Pattern** (Recommended):
- Main servo loop: Fast, real-time critical
- Grid Engine: Slower, stabilization only
- Independent operation: Grid Engine updates phase memory
- Bypass mode: Grid Engine can be disabled without affecting main loop

See: `examples/pid_grid_adapter_demo.py` (conceptual example)

---

## 🎯 Key Message

**Grid Engine is not a replacement for your CNC controller.**

**It is a stabilization module that supplements your CNC control system.**

**One-Line Summary** (for CNC industry):
> "Grid Engine is not a technology that changes the CNC controller, but a phase-based stabilization module that supplements 'vibration and memory loss' that occur during machining."

### What It Does
- ✅ Disturbance recovery after contact
- ✅ A/B axis stabilization in 5-axis machining
- ✅ Micro-vibration damping (auxiliary mode)
- ✅ Phase memory maintains stable state

### What It Does NOT Do
- ❌ Replace main servo loop
- ❌ Replace trajectory planner
- ❌ Guarantee µm-level absolute precision
- ❌ Hard real-time performance

---

## ⚠️ Current Status

**Simulation Stage**: ✅ Complete
- Mathematical model verified
- Unit contract enforced
- Integration patterns tested

**CNC Hardware Validation**: ⏳ Pending
- Real CNC testing needed
- Cycle time verification required
- Performance may vary with hardware
- Additional tuning may be required

**Production Ready**: ⏳ Not yet
- Requires CNC hardware validation
- Cycle time optimization needed
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

## 🎯 Summary

**Grid Engine for CNC**:
- Solves: Disturbance recovery, A/B axis stabilization, vibration damping
- Does NOT replace: Main servo loop, trajectory planner, precision certification
- Integration: Auxiliary loop, slower cycle, bypass mode
- Status: Simulation complete, hardware validation pending

**Ready to try?** See `examples/pid_grid_adapter_demo.py` (conceptual)

---

**Author**: GNJz  
**Made in GNJz**  
**Version**: v0.4.0-alpha  
**License**: MIT License  
**Status**: Simulation Complete, CNC Hardware Validation Pending


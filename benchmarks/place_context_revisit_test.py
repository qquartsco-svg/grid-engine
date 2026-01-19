"""
Place/Context 재방문 효과 벤치마크 (Place/Context Revisit Benchmark)

목적:
- Repeatability(동일 궤적 반복)에서는 Place/Context가 논리적으로 불리할 수 있음
- Place/Context의 강점은 **재방문(Place revisit)**, **컨텍스트 분리(Context split)**, **Replay 기반 학습**에서 나타남

시나리오:
1) Place A에 접근 → 안정 구간에서 오차(편향) 기록(Online: 기록만)
2) 휴지기(Replay) → 안정 구간만 재생하여 Place bias 학습(Replay: 학습만)
3) 다른 곳으로 이동 (Place B)
4) 다시 Place A로 재방문 → 학습된 Place bias로 오차가 줄어드는지 평가

비교군:
- PID only
- PID + Grid (Persistent Bias only)  (use_place_cells=False)
- PID + Grid (Place+Replay+Blending) (use_place_cells=True, replay_enabled=True)

측정 지표:
- 재방문 시 최종 오차 감소율
- A 재방문 구간의 표준편차(σ) 변화

Author: GNJz
Created: 2026-01-20
Made in GNJz
License: MIT License
"""

import sys
from pathlib import Path
from typing import Dict, Tuple, List, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import warnings
import logging

from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DConfig

warnings.filterwarnings("ignore")
logging.getLogger("matplotlib").setLevel(logging.ERROR)


class PIDController:
    def __init__(self, kp: float = 0.5, ki: float = 0.05, kd: float = 0.005, integral_limit: float = 0.01):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_limit = integral_limit
        self.integral = np.zeros(5)
        self.prev_error = np.zeros(5)

    def control(self, setpoint: np.ndarray, current: np.ndarray) -> np.ndarray:
        error = setpoint - current
        self.integral += error
        if self.integral_limit is not None:
            self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)
        derivative = error - self.prev_error
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

    def reset(self):
        self.integral[:] = 0.0
        self.prev_error[:] = 0.0


class GridAdapter:
    def __init__(
        self,
        setpoint: np.ndarray,
        enable_place: bool,
        enable_context: bool,
        replay_enabled: bool,
    ):
        self.grid = Grid5DEngine(
            config=Grid5DConfig(),
            initial_x=setpoint[0],
            initial_y=setpoint[1],
            initial_z=setpoint[2],
            initial_theta_a=setpoint[3],
            initial_theta_b=setpoint[4],
        )
        self.grid.set_target(setpoint)
        self._last_setpoint = setpoint.copy()
        self.grid.use_place_cells = enable_place
        self.grid.use_context_binder = enable_context
        if hasattr(self.grid, "replay_enabled"):
            self.grid.replay_enabled = replay_enabled
        self.pid = PIDController()
        self.step_counter = 0
        self.slow_update_cycle = 5

    def step(self, setpoint: np.ndarray, current: np.ndarray, external_state: Dict) -> np.ndarray:
        # ✅ 중요: 외부 setpoint 변경을 GridEngine 내부 target(stable_state)에도 동기화
        # set_target()은 bias_estimate를 리셋하므로, 시나리오 상 '목표 변경' 시점에만 호출
        if not np.allclose(setpoint, self._last_setpoint):
            self.grid.set_target(setpoint)
            self._last_setpoint = setpoint.copy()
            # PID 적분항도 리셋(목표 변경 시 windup 방지)
            self.pid.reset()

        self.step_counter += 1
        if self.step_counter % self.slow_update_cycle == 0:
            if hasattr(self.grid, "set_external_state"):
                self.grid.set_external_state(external_state)
            self.grid.update(current)
        reference_correction = self.grid.provide_reference()
        bias_mag = np.linalg.norm(reference_correction)
        correction_weight = min(1.0, 0.2 + bias_mag * 20.0)
        setpoint_corrected = setpoint + reference_correction * correction_weight
        return self.pid.control(setpoint_corrected, current)


def run_episode(
    controller: str,
    setpoint: np.ndarray,
    n_steps: int,
    adapter: Optional[GridAdapter] = None,
    external_state: Optional[Dict] = None,
    injected_bias: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, List[float]]:
    external_state = external_state or {}
    state = setpoint.copy()
    pid = PIDController()
    errors: List[float] = []
    injected_bias = injected_bias if injected_bias is not None else np.zeros(5)

    for _ in range(n_steps):
        # 관측 노이즈(고주파) + 구조적 편향(저주파) 주입
        state += np.random.normal(0, 1e-4, 5) + injected_bias
        if controller == "pid":
            u = pid.control(setpoint, state)
        else:
            assert adapter is not None
            u = adapter.step(setpoint, state, external_state)
        state += u * 0.1
        errors.append(float(np.linalg.norm(setpoint - state)))

    return state, errors


def main():
    print("\n" + "=" * 70)
    print("Place/Context 재방문 효과 벤치마크 (Revisit Test)")
    print("=" * 70)

    A = np.array([1.0, 0.5, 0.3, 10.0, 5.0])
    B = np.array([1.2, 0.3, 0.4, 12.0, 6.0])

    steps_warm = 120
    steps_move = 80
    steps_return = 120

    # ✅ 핵심: Place/Replay가 \"학습해서 이득\"을 보려면
    # 재방문 대상 Place(A)에만 구조적 편향(저주파 drift)을 지속 주입해야 함
    # (노이즈만 있으면 학습해도 이득이 거의 없음)
    A_BIAS = np.array([2e-4, 0.0, 0.0, 0.0, 0.0])  # A 구간에만 x축 +0.0002m/step
    B_BIAS = np.zeros(5)  # B 구간은 편향 없음

    # PID only
    _, _ = run_episode("pid", A, steps_warm, injected_bias=A_BIAS)
    _, _ = run_episode("pid", B, steps_move, injected_bias=B_BIAS)
    _, err_pid_A2 = run_episode("pid", A, steps_return, injected_bias=A_BIAS)

    # Persistent Bias only
    pb = GridAdapter(A, enable_place=False, enable_context=False, replay_enabled=False)
    _, _ = run_episode("grid", A, steps_warm, pb, external_state={"op": "A"}, injected_bias=A_BIAS)
    _, _ = run_episode("grid", B, steps_move, pb, external_state={"op": "B"}, injected_bias=B_BIAS)
    _, err_pb_A2 = run_episode("grid", A, steps_return, pb, external_state={"op": "A"}, injected_bias=A_BIAS)

    # Place + Replay
    pc = GridAdapter(A, enable_place=True, enable_context=False, replay_enabled=True)
    _, _ = run_episode("grid", A, steps_warm, pc, external_state={"op": "A"}, injected_bias=A_BIAS)
    if hasattr(pc.grid, "state"):
        pc.grid.state.t_ms += 2500
        pc.grid.update(A)
    _, _ = run_episode("grid", B, steps_move, pc, external_state={"op": "B"}, injected_bias=B_BIAS)
    if hasattr(pc.grid, "state"):
        pc.grid.state.t_ms += 2500
        pc.grid.update(B)
    _, err_pc_A2 = run_episode("grid", A, steps_return, pc, external_state={"op": "A"}, injected_bias=A_BIAS)

    def summarize(err: List[float]) -> Tuple[float, float]:
        arr = np.array(err)
        return float(np.mean(arr)), float(np.std(arr))

    pid_mean, pid_std = summarize(err_pid_A2)
    pb_mean, pb_std = summarize(err_pb_A2)
    pc_mean, pc_std = summarize(err_pc_A2)

    print("\n" + "=" * 70)
    print("결과 (A 재방문 구간)")
    print("=" * 70)
    print(f"{'시스템':<28} {'mean_err':>12} {'std_err':>12}")
    print("-" * 56)
    print(f"{'PID Only':<28} {pid_mean:>12.6f} {pid_std:>12.6f}")
    print(f"{'PID + Persistent Bias':<28} {pb_mean:>12.6f} {pb_std:>12.6f}")
    print(f"{'PID + Place(+Replay)':<28} {pc_mean:>12.6f} {pc_std:>12.6f}")
    print()

    pb_imp = (pid_mean - pb_mean) / pid_mean * 100.0 if pid_mean > 0 else 0.0
    pc_imp = (pid_mean - pc_mean) / pid_mean * 100.0 if pid_mean > 0 else 0.0
    print("개선율 (mean_err 기준, PID 대비):")
    print(f"  Persistent Bias: {pb_imp:+.1f}%")
    print(f"  Place(+Replay):  {pc_imp:+.1f}%")
    print()

    print("실행:")
    print("  python3 benchmarks/place_context_revisit_test.py")
    print()


if __name__ == "__main__":
    main()



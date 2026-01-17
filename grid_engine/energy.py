"""
Energy Function
에너지 계산 및 dE/dt 체크 (진단 전용, 코어 의존 X)

이 모듈은 Grid Engine의 에너지 함수를 계산하고 안정성을 진단합니다.
연속 어트랙터 네트워크(Continuous Attractor Network)의 에너지 함수를 기반으로 합니다.

핵심 개념:
    에너지 함수: E = E_phase + E_kinetic
        - E_phase: 위상 에너지 (위상 변위의 제곱)
        - E_kinetic: 운동 에너지 (속도의 제곱)
    
    에너지 감소: dE/dt ≤ 0
        - 안정적인 시스템은 에너지가 시간에 따라 감소합니다
        - 이는 Attractor 동역학의 특성입니다
    
    안정성 점수: [0, 1] 범위의 안정성 측정값

수학적 배경:
    Hopfield 네트워크와 유사한 에너지 함수를 사용합니다.
    에너지 함수의 최소값은 Attractor 상태에 해당합니다.
    시스템이 안정적이면 에너지가 감소합니다.

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from typing import Optional, Tuple
from .types import GridState, GridDiagnostics
from .config import GridEngineConfig


def calculate_energy(
    state: GridState,
    config: GridEngineConfig,
    ring_energy_x: Optional[float] = None,
    ring_energy_y: Optional[float] = None
) -> float:
    """
    에너지 함수 계산
    
    E = Ex + Ey (X, Y 방향 에너지 합)
    
    Args:
        state: 현재 상태
        config: 설정
        ring_energy_x: X 방향 Ring 에너지 (선택적)
        ring_energy_y: Y 방향 Ring 에너지 (선택적)
    
    Returns:
        총 에너지
    """
    # Ring 에너지가 제공되면 사용
    if ring_energy_x is not None and ring_energy_y is not None:
        return ring_energy_x + ring_energy_y
    
    # 기본 에너지 (위상 기반)
    # E = ½(φx² + φy²) + ½(vx² + vy²)
    phase_energy = 0.5 * (state.phi_x ** 2 + state.phi_y ** 2)
    kinetic_energy = 0.5 * (state.v_x ** 2 + state.v_y ** 2)
    
    return phase_energy + kinetic_energy


def check_energy_decrease(
    energy_prev: float,
    energy_curr: float,
    dt_ms: float
) -> tuple[bool, float]:
    """
    에너지 감소 확인
    
    dE/dt ≤ 0 확인
    
    Args:
        energy_prev: 이전 에너지
        energy_curr: 현재 에너지
        dt_ms: 시간 간격 [ms]
    
    Returns:
        (is_decreasing, dE_dt)
    """
    if dt_ms <= 0:
        return False, 0.0
    
    dE_dt = (energy_curr - energy_prev) / dt_ms
    is_decreasing = dE_dt <= 0.0
    
    return is_decreasing, dE_dt


def calculate_stability_score(
    state: GridState,
    config: GridEngineConfig
) -> float:
    """
    안정성 점수 계산
    
    Args:
        state: 현재 상태
        config: 설정
    
    Returns:
        안정성 점수 [0, 1]
    """
    # 위상 안정성 (주기적 경계 조건 준수)
    phi_x_normalized = state.phi_x % config.phase_wrap
    phi_y_normalized = state.phi_y % config.phase_wrap
    
    phi_x_stable = abs(state.phi_x - phi_x_normalized) < 1e-6
    phi_y_stable = abs(state.phi_y - phi_y_normalized) < 1e-6
    
    # 속도 안정성 (과도한 속도 방지)
    v_magnitude = (state.v_x ** 2 + state.v_y ** 2) ** 0.5
    v_stable = v_magnitude < 10.0  # 임계값 (설정 가능)
    
    # 종합 안정성 점수
    stability = 1.0 if (phi_x_stable and phi_y_stable and v_stable) else 0.0
    
    return stability


def compute_diagnostics(
    state: GridState,
    state_prev: GridState,
    config: GridEngineConfig,
    ring_energy_x: Optional[float] = None,
    ring_energy_y: Optional[float] = None
) -> GridDiagnostics:
    """
    진단 정보 계산
    
    Args:
        state: 현재 상태
        state_prev: 이전 상태
        config: 설정
        ring_energy_x: X 방향 Ring 에너지 (선택적)
        ring_energy_y: Y 방향 Ring 에너지 (선택적)
    
    Returns:
        진단 정보
    """
    # 에너지 계산
    energy_curr = calculate_energy(state, config, ring_energy_x, ring_energy_y)
    energy_prev = calculate_energy(state_prev, config, ring_energy_x, ring_energy_y)
    
    # 에너지 변화 확인
    dt_ms = state.t_ms - state_prev.t_ms
    is_decreasing, dE_dt = check_energy_decrease(energy_prev, energy_curr, dt_ms)
    
    # 안정성 점수
    stability_score = calculate_stability_score(state, config)
    
    # 위상 안정성
    phi_x_stability = 1.0 if abs(state.phi_x - state_prev.phi_x) < 0.1 else 0.0
    phi_y_stability = 1.0 if abs(state.phi_y - state_prev.phi_y) < 0.1 else 0.0
    
    # 수치 안정성
    dt_ratio = config.dt_ms / config.tau_ms
    is_stable = dt_ratio < config.max_dt_ratio
    
    return GridDiagnostics(
        energy=energy_curr,
        energy_change=dE_dt,
        energy_decreasing=is_decreasing,
        stability_score=stability_score,
        phi_x_stability=phi_x_stability,
        phi_y_stability=phi_y_stability,
        dt_ratio=dt_ratio,
        is_stable=is_stable
    )


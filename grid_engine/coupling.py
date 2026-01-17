"""
Ring ⊗ Ring 직교 결합
위상 정규화 및 좌표 변환

이 모듈은 Grid Engine의 위상(Phase)과 좌표(Coordinate) 간 변환을 담당합니다.
주기적 경계 조건(Periodic Boundary Condition)을 처리합니다.

핵심 개념:
    위상(Phase): Ring의 내부 상태 [0, 2π) [rad]
    좌표(Coordinate): 외부 세계의 위치 [m]
    변환 관계: x = φx · (Lx / 2π), φx = x · (2π / Lx)

수학적 배경:
    Grid Engine은 토러스(Torus) 공간 T² = S¹ × S¹에서 동작합니다.
    위상 φ ∈ [0, 2π)는 주기적 경계 조건을 만족합니다.
    즉, φ ≡ φ + 2πn (n은 정수)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from typing import Tuple
from .types import GridState
from .config import GridEngineConfig


def normalize_phase(phi: float, phase_wrap: float) -> float:
    """
    위상 정규화 (주기적 경계 조건)
    
    위상이 주기적 경계 조건을 만족하도록 정규화합니다.
    토러스(Torus) 공간의 특성상 위상은 [0, 2π) 범위로 감싸집니다.
    
    수학적 의미:
        위상 φ는 주기적: φ ≡ φ + 2πn (n은 정수)
        정규화: φ_norm = φ mod 2π ∈ [0, 2π)
    
    수식:
        φ_norm = φ mod phase_wrap
        여기서 phase_wrap = 2π [rad]
    
    예시:
        φ = 3π → φ_norm = 3π mod 2π = π
        φ = -π/2 → φ_norm = -π/2 mod 2π = 3π/2
    
    Args:
        phi: 원본 위상 [rad] (임의의 값)
        phase_wrap: 위상 범위 (일반적으로 2π [rad])
    
    Returns:
        정규화된 위상 [0, phase_wrap) [rad]
    
    Author: [작성자 시그니처]
    Created: 2026-01
    """
    return phi % phase_wrap


def phase_to_coordinate(
    phi_x: float,
    phi_y: float,
    config: GridEngineConfig
) -> Tuple[float, float]:
    """
    위상 → 좌표 변환
    
    내부 위상(Phase)을 외부 좌표(Coordinate)로 변환합니다.
    Grid Engine의 내부 상태를 외부 세계의 위치로 투영합니다.
    
    수학적 배경:
        Grid Engine은 토러스 T² = S¹ × S¹에서 동작합니다.
        위상 φ ∈ [0, 2π)는 주기적 공간의 위치를 나타냅니다.
        좌표 x ∈ [0, L)는 실제 공간의 위치를 나타냅니다.
    
    변환 수식:
        x = φx · (Lx / 2π)
        y = φy · (Ly / 2π)
        
        여기서:
            - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
            - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
            - 2π = phase_wrap: 위상 범위 [rad]
    
    단위 분석:
        x [m] = φx [rad] * (Lx [m] / 2π [rad])
        y [m] = φy [rad] * (Ly [m] / 2π [rad])
    
    물리적 의미:
        위상 2π [rad]가 실제 공간 L [m]에 대응됩니다.
        예: L = 10.0 m → 2π rad = 10.0 m → 1 rad ≈ 1.59 m
    
    Args:
        phi_x: X 방향 위상 [0, 2π) [rad]
        phi_y: Y 방향 위상 [0, 2π) [rad]
        config: Grid Engine 설정
    
    Returns:
        (x, y) 좌표 [m]
            - x: X 방향 좌표 [m]
            - y: Y 방향 좌표 [m]
    
    Author: [작성자 시그니처]
    Created: 2026-01
    """
    # 변환 수식: x = φx · (Lx / 2π)
    x = phi_x * (config.spatial_scale_x / config.phase_wrap)
    y = phi_y * (config.spatial_scale_y / config.phase_wrap)
    return x, y


def coordinate_to_phase(
    x: float,
    y: float,
    config: GridEngineConfig
) -> Tuple[float, float]:
    """
    좌표 → 위상 변환
    
    외부 좌표(Coordinate)를 내부 위상(Phase)으로 변환합니다.
    외부 세계의 위치를 Grid Engine의 내부 상태로 투영합니다.
    
    수학적 배경:
        phase_to_coordinate()의 역변환입니다.
        좌표 x ∈ [0, L) → 위상 φ ∈ [0, 2π)
    
    변환 수식:
        φx = x · (2π / Lx)
        φy = y · (2π / Ly)
        
        여기서:
            - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
            - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
            - 2π = phase_wrap: 위상 범위 [rad]
    
    단위 분석:
        φx [rad] = x [m] * (2π [rad] / Lx [m])
        φy [rad] = y [m] * (2π [rad] / Ly [m])
    
    물리적 의미:
        실제 공간 L [m]가 위상 2π [rad]에 대응됩니다.
        예: L = 10.0 m → 10.0 m = 2π rad → 1 m ≈ 0.628 rad
    
    Args:
        x: X 방향 좌표 [m]
        y: Y 방향 좌표 [m]
        config: Grid Engine 설정
    
    Returns:
        (phi_x, phi_y) 위상 [rad]
            - phi_x: X 방향 위상 [rad] (정규화되지 않음)
            - phi_y: Y 방향 위상 [rad] (정규화되지 않음)
        
        주의: 반환된 위상은 [0, 2π) 범위를 벗어날 수 있습니다.
              normalize_phase()를 사용하여 정규화해야 합니다.
    
    Author: [작성자 시그니처]
    Created: 2026-01
    """
    # 변환 수식: φx = x · (2π / Lx)
    phi_x = x * (config.phase_wrap / config.spatial_scale_x)
    phi_y = y * (config.phase_wrap / config.spatial_scale_y)
    return phi_x, phi_y


def update_state_from_phases(
    state: GridState,
    phi_x: float,
    phi_y: float,
    v_x: float,
    v_y: float,
    config: GridEngineConfig
) -> GridState:
    """
    위상으로부터 상태 업데이트
    
    Args:
        state: 현재 상태
        phi_x: 새로운 X 위상
        phi_y: 새로운 Y 위상
        v_x: 새로운 X 속도
        v_y: 새로운 Y 속도
        config: 설정
    
    Returns:
        업데이트된 상태
    """
    # 위상 정규화
    phi_x = normalize_phase(phi_x, config.phase_wrap)
    phi_y = normalize_phase(phi_y, config.phase_wrap)
    
    # 좌표 변환
    x, y = phase_to_coordinate(phi_x, phi_y, config)
    
    # 상태 업데이트
    return GridState(
        phi_x=phi_x,
        phi_y=phi_y,
        x=x,
        y=y,
        v_x=v_x,
        v_y=v_y,
        a_x=state.a_x,
        a_y=state.a_y,
        t_ms=state.t_ms
    )


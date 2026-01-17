"""
Grid Engine 3D Types
3D 데이터 클래스 정의 (State/Input/Output/Diagnostics)

3D 확장: Ring X ⊗ Ring Y ⊗ Ring Z
위상 공간: T³ = S¹ × S¹ × S¹ (토러스, 3차원)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
License: MIT License
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Grid3DState:
    """
    Grid 3D Engine 내부 상태
    
    내부 상태: 위상 벡터 (φx, φy, φz)
    외부 표현: 공간 좌표 (x, y, z)
    
    3D 확장:
        - 2D: (φx, φy) → (x, y)
        - 3D: (φx, φy, φz) → (x, y, z)
    """
    # 위상 (내부 상태)
    phi_x: float  # X 방향 위상 [0, 2π) [rad]
    phi_y: float  # Y 방향 위상 [0, 2π) [rad]
    phi_z: float  # Z 방향 위상 [0, 2π) [rad] (새로 추가)
    
    # 좌표 (외부 표현)
    x: float  # X 좌표 [m]
    y: float  # Y 좌표 [m]
    z: float  # Z 좌표 [m] (새로 추가)
    
    # 속도
    v_x: float  # X 방향 속도 [m/s]
    v_y: float  # Y 방향 속도 [m/s]
    v_z: float  # Z 방향 속도 [m/s] (새로 추가)
    
    # 가속도
    a_x: float  # X 방향 가속도 [m/s²]
    a_y: float  # Y 방향 가속도 [m/s²]
    a_z: float  # Z 방향 가속도 [m/s²] (새로 추가)
    
    # 시간
    t_ms: float  # 현재 시간 [ms]
    
    def __post_init__(self):
        """
        위상 범위 검증 (3D)
        
        주의: config.phase_wrap을 사용해야 하지만,
        dataclass 초기화 시점에는 config가 없으므로
        기본값 2π를 사용합니다.
        실제 정규화는 coupling.normalize_phase()에서 수행됩니다.
        """
        # 위상 주기적 경계 조건 (기본값 2π 사용)
        phase_wrap_default = 2.0 * 3.141592653589793
        self.phi_x = self.phi_x % phase_wrap_default
        self.phi_y = self.phi_y % phase_wrap_default
        self.phi_z = self.phi_z % phase_wrap_default  # Z 위상 추가


@dataclass
class Grid3DInput:
    """
    Grid 3D Engine 입력
    
    속도/가속도 벡터 입력 (3D)
    
    3D 확장:
        - 2D: (v_x, v_y), (a_x, a_y)
        - 3D: (v_x, v_y, v_z), (a_x, a_y, a_z)
    """
    # 속도
    v_x: float  # X 방향 속도 [m/s]
    v_y: float  # Y 방향 속도 [m/s]
    v_z: float  # Z 방향 속도 [m/s] (새로 추가)
    
    # 가속도 (선택적)
    a_x: Optional[float] = None  # X 방향 가속도 [m/s²]
    a_y: Optional[float] = None  # Y 방향 가속도 [m/s²]
    a_z: Optional[float] = None  # Z 방향 가속도 [m/s²] (새로 추가)
    
    # 외부 편향 (선택적)
    external_bias: Optional[Tuple[float, float, float]] = None  # (bias_x, bias_y, bias_z)


@dataclass
class Grid3DOutput:
    """
    Grid 3D Engine 출력
    
    외부 표현: 좌표 (x, y, z)
    내부 상태: 위상 (φx, φy, φz)
    
    3D 확장:
        - 2D: (x, y), (φx, φy)
        - 3D: (x, y, z), (φx, φy, φz)
    """
    # 좌표 (외부 표현)
    x: float  # X 좌표 [m]
    y: float  # Y 좌표 [m]
    z: float  # Z 좌표 [m] (새로 추가)
    
    # 위상 (내부 상태)
    phi_x: float  # X 방향 위상 [0, 2π) [rad]
    phi_y: float  # Y 방향 위상 [0, 2π) [rad]
    phi_z: float  # Z 방향 위상 [0, 2π) [rad] (새로 추가)
    
    # 안정성 점수 (선택적)
    stability_score: Optional[float] = None  # [0, 1]
    
    # 에너지 (선택적)
    energy: Optional[float] = None


@dataclass
class Grid3DDiagnostics:
    """
    Grid 3D Engine 진단 정보
    
    에너지, 안정성, 오차 등 진단용 데이터 (3D)
    
    3D 확장:
        - 2D: phi_x_stability, phi_y_stability
        - 3D: phi_x_stability, phi_y_stability, phi_z_stability
    """
    # 에너지
    energy: float  # 현재 에너지
    energy_change: float  # 에너지 변화 (dE/dt)
    energy_decreasing: bool  # 에너지 감소 여부
    
    # 안정성
    stability_score: float  # 안정성 점수 [0, 1]
    
    # 위상 안정성 (3D)
    phi_x_stability: float  # X 위상 안정성
    phi_y_stability: float  # Y 위상 안정성
    phi_z_stability: float  # Z 위상 안정성 (새로 추가)
    
    # 수치 안정성
    dt_ratio: float  # dt / tau 비율
    is_stable: bool  # 수치 안정성 여부


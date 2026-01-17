"""
Grid Engine 4D Types
4D 타입 정의 (독립 모듈)

이 모듈은 Grid 4D Engine의 타입을 정의합니다.

4D 확장:
    - 2D: GridState, GridInput, GridOutput (X, Y)
    - 3D: Grid3DState, Grid3DInput, Grid3DOutput (X, Y, Z)
    - 4D: Grid4DState, Grid4DInput, Grid4DOutput (X, Y, Z, W) ✨ NEW

핵심 구조:
    Grid 4D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W
    위상 공간: T⁴ = S¹ × S¹ × S¹ × S¹

수학적 배경:
    위상 벡터: Φ = (φx, φy, φz, φw) ∈ [0, 2π)⁴
    좌표 벡터: r = (x, y, z, w) ∈ [0, L)⁴

상세 설명:
    - docs/4D_CONCEPT_AND_EQUATIONS.md (4D 개념 및 수식)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

from dataclasses import dataclass
from typing import Optional
from .config_4d import Grid4DConfig


@dataclass
class Grid4DState:
    """
    Grid 4D 상태
    
    4D 위상 공간의 상태를 나타냅니다.
    
    4D 확장:
        - 2D: (φx, φy), (x, y), (vx, vy), (ax, ay)
        - 3D: (φx, φy, φz), (x, y, z), (vx, vy, vz), (ax, ay, az)
        - 4D: (φx, φy, φz, φw), (x, y, z, w), (vx, vy, vz, vw), (ax, ay, az, aw) ✨ NEW
    
    위상 공간:
        T⁴ = S¹ × S¹ × S¹ × S¹ (4차원 토러스)
        위상: Φ = (φx, φy, φz, φw) ∈ [0, 2π)⁴
    
    좌표 공간:
        r = (x, y, z, w) ∈ [0, Lx) × [0, Ly) × [0, Lz) × [0, Lw)
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 위상 (내부 상태) [rad]
    phi_x: float  # X 방향 위상 [0, 2π) [rad]
    phi_y: float  # Y 방향 위상 [0, 2π) [rad]
    phi_z: float  # Z 방향 위상 [0, 2π) [rad]
    phi_w: float  # W 방향 위상 [0, 2π) [rad] ✨ NEW
    
    # 좌표 (외부 표현) [m]
    # 주의: Grid Engine은 위상만 관리, 좌표는 projector가 계산
    x: float  # X 좌표 [m]
    y: float  # Y 좌표 [m]
    z: float  # Z 좌표 [m]
    w: float  # W 좌표 [m] ✨ NEW
    
    # 속도 [m/s]
    v_x: float  # X 방향 속도 [m/s]
    v_y: float  # Y 방향 속도 [m/s]
    v_z: float  # Z 방향 속도 [m/s]
    v_w: float  # W 방향 속도 [m/s] ✨ NEW
    
    # 가속도 [m/s²]
    a_x: float  # X 방향 가속도 [m/s²]
    a_y: float  # Y 방향 가속도 [m/s²]
    a_z: float  # Z 방향 가속도 [m/s²]
    a_w: float  # W 방향 가속도 [m/s²] ✨ NEW
    
    # 시간 [ms]
    t_ms: float  # 경과 시간 [ms]
    
    def __post_init__(self):
        """
        상태 초기화 후 검증
        
        위상이 [0, 2π) 범위에 있는지 확인합니다.
        """
        from ...common.coupling import normalize_phase
        from .config_4d import Grid4DConfig
        
        config = Grid4DConfig()
        phase_wrap = config.phase_wrap
        
        # 위상 정규화 (4D)
        self.phi_x = normalize_phase(self.phi_x, phase_wrap)
        self.phi_y = normalize_phase(self.phi_y, phase_wrap)
        self.phi_z = normalize_phase(self.phi_z, phase_wrap)
        self.phi_w = normalize_phase(self.phi_w, phase_wrap)  # W 방향 추가


@dataclass
class Grid4DInput:
    """
    Grid 4D 입력
    
    4D 경로 통합을 위한 입력 데이터입니다.
    
    4D 확장:
        - 2D: (vx, vy), (ax, ay)
        - 3D: (vx, vy, vz), (ax, ay, az)
        - 4D: (vx, vy, vz, vw), (ax, ay, az, aw) ✨ NEW
    
    뉴턴 제2법칙:
        속도: v = (vx, vy, vz, vw) [m/s]
        가속도: a = (ax, ay, az, aw) [m/s²]
        F = ma → a = dv/dt
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 속도 [m/s] (필수)
    v_x: float  # X 방향 속도 [m/s]
    v_y: float  # Y 방향 속도 [m/s]
    v_z: float  # Z 방향 속도 [m/s]
    v_w: float  # W 방향 속도 [m/s] ✨ NEW
    
    # 가속도 [m/s²] (선택적)
    a_x: Optional[float] = None  # X 방향 가속도 [m/s²]
    a_y: Optional[float] = None  # Y 방향 가속도 [m/s²]
    a_z: Optional[float] = None  # Z 방향 가속도 [m/s²]
    a_w: Optional[float] = None  # W 방향 가속도 [m/s²] ✨ NEW


@dataclass
class Grid4DOutput:
    """
    Grid 4D 출력
    
    4D Grid Engine의 출력 데이터입니다.
    
    4D 확장:
        - 2D: (x, y), (φx, φy)
        - 3D: (x, y, z), (φx, φy, φz)
        - 4D: (x, y, z, w), (φx, φy, φz, φw) ✨ NEW
    
    좌표:
        좌표는 projector가 계산한 값입니다.
        Grid Engine은 위상만 관리하고, 좌표 투영은 관측자(projector)의 책임입니다.
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 좌표 [m] (projector가 계산)
    x: float  # X 좌표 [m]
    y: float  # Y 좌표 [m]
    z: float  # Z 좌표 [m]
    w: float  # W 좌표 [m] ✨ NEW
    
    # 위상 [rad] (내부 상태)
    phi_x: float  # X 방향 위상 [rad]
    phi_y: float  # Y 방향 위상 [rad]
    phi_z: float  # Z 방향 위상 [rad]
    phi_w: float  # W 방향 위상 [rad] ✨ NEW
    
    # 진단 정보 (선택적)
    stability_score: Optional[float] = None  # 안정성 점수 [0, 1]
    energy: Optional[float] = None  # 에너지


@dataclass
class Grid4DDiagnostics:
    """
    Grid 4D 진단 정보
    
    4D Grid Engine의 진단 데이터입니다.
    
    4D 확장:
        - 2D: 위상 변화, 속도 변화, 에너지
        - 3D: 위상 변화 (3축), 속도 변화 (3축), 에너지
        - 4D: 위상 변화 (4축), 속도 변화 (4축), 에너지 ✨ NEW
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 위상 변화량 [rad]
    dphi_x: float  # X 방향 위상 변화 [rad]
    dphi_y: float  # Y 방향 위상 변화 [rad]
    dphi_z: float  # Z 방향 위상 변화 [rad]
    dphi_w: float  # W 방향 위상 변화 [rad] ✨ NEW
    
    # 속도 변화량 [m/s]
    dv_x: float  # X 방향 속도 변화 [m/s]
    dv_y: float  # Y 방향 속도 변화 [m/s]
    dv_z: float  # Z 방향 속도 변화 [m/s]
    dv_w: float  # W 방향 속도 변화 [m/s] ✨ NEW
    
    # 에너지
    energy: float  # 총 에너지
    energy_change: float  # 에너지 변화량
    
    # 안정성
    stability_score: float  # 안정성 점수 [0, 1]


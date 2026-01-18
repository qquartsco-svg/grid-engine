"""
Grid Engine 6D Types
6D 타입 정의 (독립 모듈)

이 모듈은 Grid 6D Engine의 타입을 정의합니다.

6D 확장 (6축 시스템):
    - 2D: GridState, GridInput, GridOutput (X, Y)
    - 3D: Grid3DState, Grid3DInput, Grid3DOutput (X, Y, Z)
    - 4D: Grid4DState, Grid4DInput, Grid4DOutput (X, Y, Z, W)
    - 6D: Grid6DState, Grid6DInput, Grid6DOutput (X, Y, Z, A, B, C) ✨ NEW

핵심 구조:
    Grid 6D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ⊗ Ring C
    위상 공간: T⁶ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹
    
    6축 시스템 매핑:
        - 위치 축 (3개): X, Y, Z (선형 이동)
        - 회전 축 (2개): A, B (각도 회전)

수학적 배경:
    위상 벡터: Φ = (φx, φy, φz, φa, φb, φc) ∈ [0, 2π)⁵
    위치 벡터: r = (x, y, z) ∈ [0, L)³
    각도 벡터: θ = (θa, θb, θc) ∈ [0, 360°)² 또는 [-180°, 180°)²

상세 설명:
    - docs/6D_CONCEPT_AND_EQUATIONS.md (6D 개념 및 수식)
    - docs/5AXIS_CNC_APPLICATION.md (6축 시스템 응용)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (6D extension)
License: MIT License
"""

from dataclasses import dataclass
from typing import Optional
from .config_6d import Grid6DConfig


@dataclass
class Grid6DState:
    """
    Grid 6D 상태
    
    6D 위상 공간의 상태를 나타냅니다.
    
    6D 확장 (6축 시스템):
        - 2D: (φx, φy), (x, y), (vx, vy), (ax, ay)
        - 3D: (φx, φy, φz), (x, y, z), (vx, vy, vz), (ax, ay, az)
        - 4D: (φx, φy, φz, φw), (x, y, z, w), (vx, vy, vz, vw), (ax, ay, az, aw)
        - 6D: (φx, φy, φz, φa, φb, φc), (x, y, z, θa, θb, θc), (vx, vy, vz, va, vb), (ax, ay, az, αa, αb) ✨ NEW
    
    위상 공간:
        T⁶ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹ (5차원 토러스)
        위상: Φ = (φx, φy, φz, φa, φb, φc) ∈ [0, 2π)⁵
    
    좌표 공간:
        위치: r = (x, y, z) ∈ [0, Lx) × [0, Ly) × [0, Lz) [m]
        각도: θ = (θa, θb, θc) ∈ [0, 360°)² 또는 [-180°, 180°)² [deg]
    
    6축 시스템 매핑:
        - X, Y, Z: 위치 축 (선형 이동) [m]
        - A, B: 회전 축 (각도 회전) [deg]
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 위상 (내부 상태) [rad]
    phi_x: float  # X 방향 위상 [0, 2π) [rad] (위치)
    phi_y: float  # Y 방향 위상 [0, 2π) [rad] (위치)
    phi_z: float  # Z 방향 위상 [0, 2π) [rad] (위치)
    phi_a: float  # A 방향 위상 [0, 2π) [rad] (회전) ✨ NEW
    phi_b: float  # B 방향 위상
    phi_c: float  # C 방향 위상 [0, 2π) [rad] (회전) ✨ NEW
    
    # 좌표 (외부 표현)
    # 주의: Grid Engine은 위상만 관리, 좌표는 projector가 계산
    x: float  # X 좌표 [m] (위치)
    y: float  # Y 좌표 [m] (위치)
    z: float  # Z 좌표 [m] (위치)
    theta_a: float  # A축 각도 [deg] (회전) ✨ NEW
    theta_b: float  # B축 각도
    theta_c: float  # C축 각도 [deg] (회전) ✨ NEW
    
    # 속도 [m/s] (위치) / [rad/s] (회전, 내부 단위)
    # ⚠️ 중요: 내부 상태는 무조건 rad 기준
    v_x: float  # X 방향 속도 [m/s]
    v_y: float  # Y 방향 속도 [m/s]
    v_z: float  # Z 방향 속도 [m/s]
    v_a: float  # A축 각속도 [rad/s] (내부 단위) ✨ NEW
    v_b: float  # B축 각속도
    v_c: float  # C축 각속도 [rad/s] (내부 단위) ✨ NEW
    
    # 가속도 [m/s²] (위치) / [rad/s²] (회전, 내부 단위)
    # ⚠️ 중요: 내부 상태는 무조건 rad 기준
    a_x: float  # X 방향 가속도 [m/s²]
    a_y: float  # Y 방향 가속도 [m/s²]
    a_z: float  # Z 방향 가속도 [m/s²]
    alpha_a: float  # A축 각가속도 [rad/s²] (내부 단위) ✨ NEW
    alpha_b: float  # B축 각가속도
    alpha_c: float  # C축 각가속도 [rad/s²] (내부 단위) ✨ NEW
    
    # 시간 [ms]
    t_ms: float  # 경과 시간 [ms]
    
    def __post_init__(self):
        """
        상태 초기화 후 검증
        
        위상이 [0, 2π) 범위에 있는지 확인합니다.
        """
        from ...common.coupling import normalize_phase
        from .config_6d import Grid6DConfig
        
        config = Grid6DConfig()
        phase_wrap = config.phase_wrap
        
        # 위상 정규화 (6D)
        self.phi_x = normalize_phase(self.phi_x, phase_wrap)
        self.phi_y = normalize_phase(self.phi_y, phase_wrap)
        self.phi_z = normalize_phase(self.phi_z, phase_wrap)
        self.phi_a = normalize_phase(self.phi_a, phase_wrap)  # A 방향 추가
        self.phi_b = normalize_phase(self.phi_b, phase_wrap)  # B 방향 추가
        self.phi_c = normalize_phase(self.phi_c, phase_wrap)  # C 방향 추가


@dataclass
class Grid6DInput:
    """
    Grid 6D 입력
    
    6D 경로 통합을 위한 입력 데이터입니다.
    
    6D 확장 (6축 시스템):
        - 2D: (vx, vy), (ax, ay)
        - 3D: (vx, vy, vz), (ax, ay, az)
        - 4D: (vx, vy, vz, vw), (ax, ay, az, aw)
        - 6D: (vx, vy, vz, va, vb), (ax, ay, az, αa, αb) ✨ NEW
    
    ⚠️ 단위 계약 (Unit Contract, 필수 준수):
        🔒 Rule 1: 입력 단위
            - 위치 축 (X, Y, Z): [m/s], [m/s²]
            - 회전 축 (A, B, C): [deg/s], [deg/s²] ← 입력은 무조건 deg 단위
        
        🔒 Rule 2: 내부 변환 (자동)
            - integrator_6d에서 입력 [deg/s, deg/s²] → 내부 [rad/s, rad/s²] 자동 변환
            - 변환 수식: v_rad = v_deg * (π / 180°), α_rad = α_deg * (π / 180°)
        
        🔒 Rule 3: 엔진 내부 (강제)
            - 모든 회전 값은 [rad], [rad/s], [rad/s²] 기준으로 처리
            - Grid6DState의 v_a, v_b, alpha_a, alpha_b는 무조건 rad 단위
        
        🔒 Rule 4: 출력 단위 (projector)
            - projector_6d에서 내부 [rad] → 출력 [deg] 변환
            - 변환 수식: θ_deg = φ_rad * (180° / π)

    뉴턴 제2법칙 (단위 일관성 필수):
        위치 축: v = (vx, vy, vz) [m/s], a = (ax, ay, az) [m/s²]
        회전 축: v = (va, vb) [deg/s] (입력) → [rad/s] (내부), α = (αa, αb) [deg/s²] (입력) → [rad/s²] (내부)
        F = ma → a = dv/dt (물리 법칙 유지)
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 속도 (필수)
    v_x: float  # X 방향 속도 [m/s] (위치)
    v_y: float  # Y 방향 속도 [m/s] (위치)
    v_z: float  # Z 방향 속도 [m/s] (위치)
    v_a: float  # A축 각속도 [deg/s] 또는 [rad/s] (회전) ✨ NEW
    v_b: float  # B축 각속도
    v_c: float  # C축 각속도 [deg/s] 또는 [rad/s] (회전) ✨ NEW
    
    # 가속도 (선택적)
    a_x: Optional[float] = None  # X 방향 가속도 [m/s²] (위치)
    a_y: Optional[float] = None  # Y 방향 가속도 [m/s²] (위치)
    a_z: Optional[float] = None  # Z 방향 가속도 [m/s²] (위치)
    alpha_a: Optional[float] = None  # A축 각가속도 [deg/s²] 또는 [rad/s²] (회전) ✨ NEW
    alpha_b: Optional[float] = None  # B축 각가속도
    alpha_c: Optional[float] = None  # C축 각가속도 [deg/s²] 또는 [rad/s²] (회전) ✨ NEW


@dataclass
class Grid6DOutput:
    """
    Grid 6D 출력
    
    6D Grid Engine의 출력 데이터입니다.
    
    6D 확장 (6축 시스템):
        - 2D: (x, y), (φx, φy)
        - 3D: (x, y, z), (φx, φy, φz)
        - 4D: (x, y, z, w), (φx, φy, φz, φw)
        - 6D: (x, y, z, θa, θb, θc), (φx, φy, φz, φa, φb, φc) ✨ NEW
    
    좌표:
        좌표는 projector가 계산한 값입니다.
        Grid Engine은 위상만 관리하고, 좌표 투영은 관측자(projector)의 책임입니다.
    
    6축 시스템 출력:
        - 위치: (x, y, z) [m]
        - 회전: (θa, θb) [deg]
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 좌표 (projector가 계산)
    x: float  # X 좌표 [m] (위치)
    y: float  # Y 좌표 [m] (위치)
    z: float  # Z 좌표 [m] (위치)
    theta_a: float  # A축 각도 [deg] (회전) ✨ NEW
    theta_b: float  # B축 각도
    theta_c: float  # C축 각도 [deg] (회전) ✨ NEW
    
    # 위상 [rad] (내부 상태)
    phi_x: float  # X 방향 위상 [rad] (위치)
    phi_y: float  # Y 방향 위상 [rad] (위치)
    phi_z: float  # Z 방향 위상 [rad] (위치)
    phi_a: float  # A 방향 위상 [rad] (회전) ✨ NEW
    phi_b: float  # B 방향 위상
    phi_c: float  # C 방향 위상 [rad] (회전) ✨ NEW
    
    # 진단 정보 (선택적)
    stability_score: Optional[float] = None  # 안정성 점수 [0, 1]
    energy: Optional[float] = None  # 에너지


@dataclass
class Grid6DDiagnostics:
    """
    Grid 6D 진단 정보
    
    6D Grid Engine의 진단 데이터입니다.
    
    6D 확장 (6축 시스템):
        - 2D: 위상 변화, 속도 변화, 에너지
        - 3D: 위상 변화 (3축), 속도 변화 (3축), 에너지
        - 4D: 위상 변화 (4축), 속도 변화 (4축), 에너지
        - 6D: 위상 변화 (5축), 속도 변화 (5축), 에너지 ✨ NEW
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 위상 변화량 [rad]
    dphi_x: float  # X 방향 위상 변화 [rad] (위치)
    dphi_y: float  # Y 방향 위상 변화 [rad] (위치)
    dphi_z: float  # Z 방향 위상 변화 [rad] (위치)
    dphi_a: float  # A 방향 위상 변화 [rad] (회전) ✨ NEW
    dphi_b: float  # B 방향 위상
    phi_c: float  # C 방향 위상 변화 [rad] (회전) ✨ NEW
    
    # 속도 변화량
    dv_x: float  # X 방향 속도 변화 [m/s] (위치)
    dv_y: float  # Y 방향 속도 변화 [m/s] (위치)
    dv_z: float  # Z 방향 속도 변화 [m/s] (위치)
    dv_a: float  # A축 각속도 변화 [deg/s] 또는 [rad/s] (회전) ✨ NEW
    dv_b: float  # B축 각속도
    v_c: float  # C축 각속도 변화 [deg/s] 또는 [rad/s] (회전) ✨ NEW
    
    # 에너지
    energy: float  # 총 에너지
    energy_change: float  # 에너지 변화량
    
    # 안정성
    stability_score: float  # 안정성 점수 [0, 1]


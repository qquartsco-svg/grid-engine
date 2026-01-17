"""
Grid 5D Engine
Ring ⊗ Ring ⊗ Ring ⊗ Ring ⊗ Ring 조립 + step()만 담당

이 모듈은 5D Grid Engine의 메인 엔진입니다.
Ring Attractor Engine 5개(X, Y, Z, A, B)를 직교 결합하여 5D 위상 공간을 구성합니다.

5D 확장 (5축 CNC):
    - 2D: Grid = Ring X ⊗ Ring Y
    - 3D: Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z
    - 4D: Grid 4D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W
    - 5D: Grid 5D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ✨ NEW

뉴턴 제2법칙과의 연관성 (5D):
    Grid 5D Engine은 뉴턴 제2법칙 (F = ma)을 5차원 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    
    물리적 대응 관계 (5D):
        위치 축 (X, Y, Z):
            물리량          Grid 5D Engine          단위
            위치 r          위상 φ (phase)           [rad]
            속도 v          속도 입력 (velocity)     [m/s]
            가속도 a        가속도 입력 (accel)      [m/s²]
            힘 F            외란 (disturbance)      [N]
        
        회전 축 (A, B):
            물리량          Grid 5D Engine          단위
            각도 θ          위상 φ (phase)           [rad]
            각속도 ω        각속도 입력 (velocity)   [deg/s] 또는 [rad/s]
            각가속도 α      각가속도 입력 (accel)    [deg/s²] 또는 [rad/s²]
            토크 τ          외란 (disturbance)      [N·m]
    
    상태 방정식 (뉴턴 역학의 이산화, 5D):
        위치 축:
            dφx/dt = vx(t)
            dφy/dt = vy(t)
            dφz/dt = vz(t)
            
            dvx/dt = ax(t)  ← 뉴턴 2법칙
            dvy/dt = ay(t)  ← 뉴턴 2법칙
            dvz/dt = az(t)  ← 뉴턴 2법칙
        
        회전 축:
            dφa/dt = va(t)
            dφb/dt = vb(t)
            
            dva/dt = αa(t)  ← 회전 운동 방정식 (τ = Iα)
            dvb/dt = αb(t)  ← 회전 운동 방정식 (τ = Iα)
    
    코드 구현:
        integrator_5d.semi_implicit_euler_5d()에서 뉴턴 2법칙을 적용
        위치 축: v_new = v_old + a * dt_s, phi_new = phi_old + v * dt_s + 0.5 * a * dt_s²
        회전 축: v_new = v_old + α * dt_s, phi_new = phi_old + v * dt_s + 0.5 * α * dt_s²
    
    상세 설명:
        - docs/NEWTONS_LAW_CONNECTION.md (뉴턴 2법칙)
        - docs/5D_CONCEPT_AND_EQUATIONS.md (5D 개념 및 수식)

핵심 아키텍처:
    Grid 5D Engine = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B
    - Ring X: X 방향 위상 관리 (φx ∈ [0, 2π)) (위치)
    - Ring Y: Y 방향 위상 관리 (φy ∈ [0, 2π)) (위치)
    - Ring Z: Z 방향 위상 관리 (φz ∈ [0, 2π)) (위치)
    - Ring A: A 방향 위상 관리 (φa ∈ [0, 2π)) (회전) ✨ NEW
    - Ring B: B 방향 위상 관리 (φb ∈ [0, 2π)) (회전) ✨ NEW
    - 직교 결합: 각 Ring은 독립적으로 동작

모듈 분리 원칙:
    - grid_5d_engine.py: 조립 + step()만 담당
    - integrator_5d.py: 수치 적분 (경로 통합, 뉴턴 2법칙, 5D)
    - coupling.py: 위상 정규화 (2D/3D/4D/5D 공통 사용 가능)
    - projector_5d.py: 좌표/각도 투영 (관측자, 5D)
    - energy.py: 에너지 계산 및 진단 (2D만 지원, 5D는 TODO)
    - adapters/ring_5d_adapter.py: Ring Engine 래핑 (5D)

알고리즘 흐름:
    1. 수치 적분: 속도/가속도 → 위상 업데이트 (뉴턴 2법칙, 5D)
    2. Ring 안정화: 위상을 Attractor에 붙잡기 (5개 Ring)
    3. 좌표/각도 투영: 위상 → 좌표/각도 변환 (projector_5d 사용)

수학적 배경:
    Grid 5D Engine은 연속 어트랙터 네트워크(Continuous Attractor Network)의
    5차원 확장입니다. 경로 통합(Path Integration)을 통해 5D 위치/각도 상태를 유지합니다.
    
    위상 공간: T⁵ = S¹ × S¹ × S¹ × S¹ × S¹ (토러스, 5차원)
    상태 방정식: dΦ/dt = v + ½a·t (5D 벡터)

상세 설명:
    - docs/5D_CONCEPT_AND_EQUATIONS.md (5D 개념 및 수식)
    - docs/5AXIS_CNC_APPLICATION.md (5축 CNC 응용)
    - docs/RING_ATTRACTOR_RELATIONSHIP.md (Ring Attractor 연관성)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

from typing import Optional
import math
from .config_5d import Grid5DConfig
from .types_5d import Grid5DState, Grid5DInput, Grid5DOutput, Grid5DDiagnostics
from .integrator_5d import semi_implicit_euler_5d
from ...common.coupling import normalize_phase
from ...common.energy import compute_diagnostics, calculate_energy  # TODO: 5D 에너지 계산으로 확장
from ...common.adapters.ring_5d_adapter import Ring5DAdapter
from ...common.adapters.ring_adapter import RingAdapterConfig
from .projector_5d import Coordinate5DProjector


class Grid5DEngine:
    """
    Grid 5D Engine
    
    Ring ⊗ Ring ⊗ Ring ⊗ Ring ⊗ Ring 구조로 5D 위치/각도 상태 유지
    
    5D 확장 (5축 CNC):
        - 2D: Ring X ⊗ Ring Y → (x, y)
        - 3D: Ring X ⊗ Ring Y ⊗ Ring Z → (x, y, z)
        - 4D: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W → (x, y, z, w)
        - 5D: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B → (x, y, z, θa, θb) ✨ NEW
    
    5축 CNC 매핑:
        - 위치 축 (3개): X, Y, Z (선형 이동) [m]
        - 회전 축 (2개): A, B (각도 회전) [deg]
    """
    
    def __init__(
        self,
        config: Optional[Grid5DConfig] = None,
        initial_x: float = 0.0,
        initial_y: float = 0.0,
        initial_z: float = 0.0,
        initial_theta_a: float = 0.0,  # 회전 각도 ✨ NEW
        initial_theta_b: float = 0.0   # 회전 각도 ✨ NEW
    ):
        """
        Grid 5D Engine 초기화
        
        Args:
            config: 설정 (None이면 기본값)
            initial_x: 초기 X 좌표 [m] (위치)
            initial_y: 초기 Y 좌표 [m] (위치)
            initial_z: 초기 Z 좌표 [m] (위치)
            initial_theta_a: 초기 A축 각도 [deg] (회전) ✨ NEW
            initial_theta_b: 초기 B축 각도 [deg] (회전) ✨ NEW
        """
        self.config = config or Grid5DConfig()
        self.config.validate()
        
        # Ring 5D Adapter 생성
        ring_cfg_x = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_x
        )
        ring_cfg_y = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_y
        )
        ring_cfg_z = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_z
        )
        ring_cfg_a = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_a
        )  # 회전 축 ✨ NEW
        ring_cfg_b = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_b
        )  # 회전 축 ✨ NEW
        self.ring_adapter = Ring5DAdapter(ring_cfg_x, ring_cfg_y, ring_cfg_z, ring_cfg_a, ring_cfg_b)
        
        # Coordinate 5D Projector 생성 (좌표/각도 투영 담당)
        self.projector = Coordinate5DProjector(self.config)
        
        # 초기 상태 설정 (5D)
        # 주의: Grid 5D Engine은 위상만 유지, 좌표/각도는 projector가 계산
        phi_x, phi_y, phi_z, phi_a, phi_b = self.projector.coordinate_to_phase(
            initial_x, initial_y, initial_z, initial_theta_a, initial_theta_b
        )
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        phi_z = normalize_phase(phi_z, self.config.phase_wrap)
        phi_a = normalize_phase(phi_a, self.config.phase_wrap)  # 회전 위상 ✨ NEW
        phi_b = normalize_phase(phi_b, self.config.phase_wrap)  # 회전 위상 ✨ NEW
        
        self.state = Grid5DState(
            phi_x=phi_x, phi_y=phi_y, phi_z=phi_z, phi_a=phi_a, phi_b=phi_b,
            x=initial_x, y=initial_y, z=initial_z,
            theta_a=initial_theta_a, theta_b=initial_theta_b,  # 회전 각도 ✨ NEW
            v_x=0.0, v_y=0.0, v_z=0.0,
            v_a=0.0, v_b=0.0,  # 회전 각속도 ✨ NEW
            a_x=0.0, a_y=0.0, a_z=0.0,
            alpha_a=0.0, alpha_b=0.0,  # 회전 각가속도 ✨ NEW
            t_ms=0.0
        )
        
        self.state_prev: Optional[Grid5DState] = None
    
    def step(self, inp: Grid5DInput) -> Grid5DOutput:
        """
        Grid 5D Engine step 함수
        
        한 스텝 실행: 5D 경로 통합 → Ring 안정화 (5개) → 5D 좌표/각도 투영
        
        알고리즘:
            1. 수치 적분 (5D): 속도/가속도 → 위상 업데이트
                - 위치 축: v_new = v_old + a * dt_s, phi_new = phi_old + v * dt_s + 0.5 * a * dt_s²
                - 회전 축: v_new = v_old + α * dt_s, phi_new = phi_old + v * dt_s + 0.5 * α * dt_s²
            2. Ring 안정화 (5개): 위상을 Attractor에 붙잡기
                - Ring X, Y, Z: 위치 위상 안정화
                - Ring A, B: 회전 위상 안정화
            3. 좌표/각도 투영: 위상 → 좌표/각도 변환
                - 위치: (x, y, z) = projector.phase_to_coordinate(phi_x, phi_y, phi_z, ...)
                - 각도: (θa, θb) = projector.phase_to_coordinate(..., phi_a, phi_b)
        
        Args:
            inp: 5D 입력 데이터
                - 위치: v_x, v_y, v_z [m/s], a_x, a_y, a_z [m/s²]
                - 회전: v_a, v_b [deg/s] 또는 [rad/s], alpha_a, alpha_b [deg/s²] 또는 [rad/s²]
        
        Returns:
            Grid5DOutput: 5D 출력 데이터
                - 위치: (x, y, z) [m]
                - 각도: (theta_a, theta_b) [deg]
                - 위상: (phi_x, phi_y, phi_z, phi_a, phi_b) [rad]
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 진단 모드: 이전 상태 저장
        if self.config.diagnostics_enabled:
            self.state_prev = Grid5DState(
                phi_x=self.state.phi_x, phi_y=self.state.phi_y, phi_z=self.state.phi_z,
                phi_a=self.state.phi_a, phi_b=self.state.phi_b,  # 회전 위상 ✨ NEW
                x=self.state.x, y=self.state.y, z=self.state.z,
                theta_a=self.state.theta_a, theta_b=self.state.theta_b,  # 회전 각도 ✨ NEW
                v_x=self.state.v_x, v_y=self.state.v_y, v_z=self.state.v_z,
                v_a=self.state.v_a, v_b=self.state.v_b,  # 회전 각속도 ✨ NEW
                a_x=self.state.a_x, a_y=self.state.a_y, a_z=self.state.a_z,
                alpha_a=self.state.alpha_a, alpha_b=self.state.alpha_b,  # 회전 각가속도 ✨ NEW
                t_ms=self.state.t_ms
            )
        
        # 1. 수치 적분 (5D): 속도/가속도 → 위상 업데이트
        # 뉴턴 2법칙 적용: 위치 축 (F = ma), 회전 축 (τ = Iα)
        new_phi_x, new_phi_y, new_phi_z, new_phi_a, new_phi_b, \
        new_v_x, new_v_y, new_v_z, new_v_a, new_v_b = semi_implicit_euler_5d(
            self.state, inp, self.config.dt_ms, self.config.tau_ms
        )
        
        # 2. Ring 안정화 (5개): 위상을 Attractor에 붙잡기
        # 위치 Ring (X, Y, Z) + 회전 Ring (A, B)
        stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_a, stabilized_phi_b, \
        energy_x, energy_y, energy_z, energy_a, energy_b = \
            self.ring_adapter.step(
                new_phi_x, new_phi_y, new_phi_z, new_phi_a, new_phi_b,
                self.config.dt_ms
            )
        
        # 위상 정규화 (5D)
        phi_x_norm = normalize_phase(stabilized_phi_x, self.config.phase_wrap)
        phi_y_norm = normalize_phase(stabilized_phi_y, self.config.phase_wrap)
        phi_z_norm = normalize_phase(stabilized_phi_z, self.config.phase_wrap)
        phi_a_norm = normalize_phase(stabilized_phi_a, self.config.phase_wrap)  # 회전 위상 ✨ NEW
        phi_b_norm = normalize_phase(stabilized_phi_b, self.config.phase_wrap)  # 회전 위상 ✨ NEW
        
        # 3. 좌표/각도 투영: 위상 → 좌표/각도 변환
        x, y, z, theta_a, theta_b = self.projector.phase_to_coordinate(
            phi_x_norm, phi_y_norm, phi_z_norm, phi_a_norm, phi_b_norm
        )
        
        # 상태 업데이트 (5D)
        self.state = Grid5DState(
            phi_x=phi_x_norm, phi_y=phi_y_norm, phi_z=phi_z_norm,
            phi_a=phi_a_norm, phi_b=phi_b_norm,  # 회전 위상 ✨ NEW
            x=x, y=y, z=z,
            theta_a=theta_a, theta_b=theta_b,  # 회전 각도 ✨ NEW
            v_x=new_v_x, v_y=new_v_y, v_z=new_v_z,
            v_a=new_v_a, v_b=new_v_b,  # 회전 각속도 [rad/s] (내부 단위) ✨ NEW
            a_x=inp.a_x if inp.a_x is not None else self.state.a_x,
            a_y=inp.a_y if inp.a_y is not None else self.state.a_y,
            a_z=inp.a_z if inp.a_z is not None else self.state.a_z,
            # ⚠️ 단위: 입력 [deg/s²] → 내부 [rad/s²] 변환
            #          state에는 rad/s² 저장 (내부 단위)
            alpha_a=math.radians(inp.alpha_a) if inp.alpha_a is not None else self.state.alpha_a,  # 회전 각가속도 [rad/s²] ✨ NEW
            alpha_b=math.radians(inp.alpha_b) if inp.alpha_b is not None else self.state.alpha_b,  # 회전 각가속도 [rad/s²] ✨ NEW
            t_ms=self.state.t_ms + self.config.dt_ms
        )
        
        # 출력 생성 (5D)
        output_x, output_y, output_z, output_theta_a, output_theta_b = self.projector.phase_to_coordinate(
            self.state.phi_x, self.state.phi_y, self.state.phi_z, self.state.phi_a, self.state.phi_b
        )
        
        output = Grid5DOutput(
            x=output_x, y=output_y, z=output_z,
            theta_a=output_theta_a, theta_b=output_theta_b,  # 회전 각도 ✨ NEW
            phi_x=self.state.phi_x, phi_y=self.state.phi_y, phi_z=self.state.phi_z,
            phi_a=self.state.phi_a, phi_b=self.state.phi_b  # 회전 위상 ✨ NEW
        )
        
        # 진단 모드: 에너지 검증 (TODO: 5D 에너지 계산으로 확장)
        if self.config.diagnostics_enabled and self.state_prev is not None:
            pass  # TODO: 5D 진단 구현
        if self.config.energy_check_enabled and self.state_prev is not None:
            pass  # TODO: 5D 에너지 검증
        
        return output
    
    def get_state(self) -> Grid5DState:
        """현재 상태 반환 (5D)"""
        return self.state
    
    def reset(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        theta_a: float = 0.0,  # 회전 각도 ✨ NEW
        theta_b: float = 0.0   # 회전 각도 ✨ NEW
    ):
        """
        상태 리셋 (5D)
        
        Args:
            x: 초기 X 좌표 [m] (위치)
            y: 초기 Y 좌표 [m] (위치)
            z: 초기 Z 좌표 [m] (위치)
            theta_a: 초기 A축 각도 [deg] (회전) ✨ NEW
            theta_b: 초기 B축 각도 [deg] (회전) ✨ NEW
        """
        phi_x, phi_y, phi_z, phi_a, phi_b = self.projector.coordinate_to_phase(x, y, z, theta_a, theta_b)
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        phi_z = normalize_phase(phi_z, self.config.phase_wrap)
        phi_a = normalize_phase(phi_a, self.config.phase_wrap)  # 회전 위상 ✨ NEW
        phi_b = normalize_phase(phi_b, self.config.phase_wrap)  # 회전 위상 ✨ NEW
        
        self.state = Grid5DState(
            phi_x=phi_x, phi_y=phi_y, phi_z=phi_z, phi_a=phi_a, phi_b=phi_b,
            x=x, y=y, z=z,
            theta_a=theta_a, theta_b=theta_b,  # 회전 각도 ✨ NEW
            v_x=0.0, v_y=0.0, v_z=0.0,
            v_a=0.0, v_b=0.0,  # 회전 각속도 ✨ NEW
            a_x=0.0, a_y=0.0, a_z=0.0,
            alpha_a=0.0, alpha_b=0.0,  # 회전 각가속도 ✨ NEW
            t_ms=0.0
        )
        # TODO: ring_adapter.reset() 구현 (5D)
        # self.ring_adapter.reset()


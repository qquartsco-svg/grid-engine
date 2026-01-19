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

from typing import Optional, Dict, Any
import math
import numpy as np
from .config_5d import Grid5DConfig
from .types_5d import Grid5DState, Grid5DInput, Grid5DOutput, Grid5DDiagnostics
from .integrator_5d import semi_implicit_euler_5d
from ...common.coupling import normalize_phase
from ...common.energy import compute_diagnostics, calculate_energy  # TODO: 5D 에너지 계산으로 확장
from ...common.adapters.ring_5d_adapter import Ring5DAdapter
from ...common.adapters.ring_adapter import RingAdapterConfig
from ...hippocampus.place_cells import PlaceCellManager  # Place Cells ✨ NEW
from ...hippocampus.context_binder import ContextBinder  # Context Binder ✨ NEW
from ...hippocampus.replay_consolidation import ReplayConsolidation  # Replay/Consolidation ✨ NEW
from ...hippocampus.learning_gate import LearningGate, LearningGateConfig  # Learning Gate ✨ NEW
from ...hippocampus.replay_buffer import ReplayBuffer, TrajectoryPoint  # Replay Buffer ✨ NEW
from ...hippocampus.universal_memory import UniversalMemory  # Universal Memory ✨ NEW
from ...cerebellum.cerebellum_engine import CerebellumEngine, CerebellumConfig  # Cerebellum ✨ NEW
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
        
        # Persistent Bias Estimator를 위한 상태
        self.stable_state: Optional[Grid5DState] = None  # 기억된 안정 상태 (목표)
        self.bias_estimate: np.ndarray = np.zeros(5)  # 전역 편향 추정 (하위 호환성) [x, y, z, theta_a, theta_b]
        self.bias_learning_rate: float = 0.01  # 편향 학습률 (저주파)
        self.update_counter: int = 0  # 업데이트 카운터 (저주파 제어용)
        self.slow_update_threshold: int = 10  # 느린 업데이트 임계값 (10 step, Place Memory 쌓기 위해) ✨ FIXED
        
        # Place Cells (장소별 독립적인 기억) ✨ NEW
        self.place_manager = PlaceCellManager(
            num_places=1000,
            phase_wrap=self.config.phase_wrap,
            quantization_level=100
        )
        self.use_place_cells: bool = False  # Place Cells 사용 여부 (기본값: False, Learning Gate로 제어) ✨ FIXED
        
        # Learning Gate (학습 조건 제어) ✨ NEW
        self.learning_gate = LearningGate(
            config=LearningGateConfig(
                default_enabled=False,  # 기본 OFF
                replay_only=True  # Replay phase에서만 학습
            )
        )
        
        # Context Binder (Place + Context 조합으로 기억 분리) ✨ NEW
        self.context_binder = ContextBinder(num_contexts=10000)
        self.use_context_binder: bool = True  # Context Binder 사용 여부 (기본값: True)
        self.external_state: Dict[str, Any] = {}  # 외부 상태 (온도, 공구, 작업 단계 등)
        
        # Replay Buffer (Online phase에서 기록만) ✨ NEW
        self.replay_buffer = ReplayBuffer(
            max_size=10000,  # 최대 버퍼 크기
            stable_window=10  # 안정성 판단 윈도우
        )
        
        # Replay/Consolidation (휴지기에 기억 재검토 및 강화) ✨ NEW
        self.replay_consolidation = ReplayConsolidation(
            replay_threshold=1.0,  # 1초 이상 휴지기 (더 빠른 트리거) ✨ FIXED
            consolidation_window=3,  # 최근 3회차 평균 (더 작은 윈도우로 조정) ✨ FIXED
            significance_threshold=0.1  # 통계적 유의성 임계값 (더 관대하게 조정) ✨ FIXED
        )
        self.use_replay_consolidation: bool = True  # Replay/Consolidation 사용 여부 (기본값: True)
        self.last_update_time_for_replay: float = 0.0  # Replay용 마지막 업데이트 시간
        self.replay_enabled: bool = True  # Replay 활성화 여부 (기본값: True) ✨ NEW
        
        # Universal Memory (범용 기억 인터페이스) ✨ NEW
        self.universal_memory = UniversalMemory(
            memory_dim=5,
            num_places=1000,
            num_contexts=10000,
            phase_wrap=self.config.phase_wrap,
            quantization_level=100
        )
        
        # Cerebellum Engine (소뇌 엔진) ✨ NEW
        self.cerebellum = CerebellumEngine(
            memory_dim=5,
            config=CerebellumConfig(
                feedforward_gain=0.5,
                trial_gain=0.3,
                variance_gain=0.2,
                memory_gain=0.4,
                correction_weight=1.0
            ),
            memory=self.universal_memory
        )
        self.use_cerebellum: bool = True  # Cerebellum 사용 여부 (기본값: True) ✨ NEW
    
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
    
    def get_phase_vector(self) -> np.ndarray:
        """
        현재 위상 벡터 반환 (Place Cells용)
        
        Returns:
            위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b] (rad)
        """
        return np.array([
            self.state.phi_x,
            self.state.phi_y,
            self.state.phi_z,
            self.state.phi_a,
            self.state.phi_b
        ])
    
    def update(self, current_state: np.ndarray) -> None:
        """
        현재 상태를 Grid Engine에 업데이트 (Persistent Bias Estimator용)
        
        아주 느린 주기로 상태를 업데이트하고, 누적 편향을 학습합니다.
        Grid Engine은 현재 상태를 위상 공간에 저장하고, 장기적인 편향을 추정합니다.
        
        Args:
            current_state: 현재 상태 [x, y, z, theta_a, theta_b]
                - x, y, z: 위치 [m]
                - theta_a, theta_b: 각도 [deg]
        
        Author: GNJz
        Created: 2026-01-20
        Updated: 2026-01-20 (Persistent Bias Estimator로 재정의)
        Made in GNJz
        """
        self.update_counter += 1
        
        # ⚠️ 중요: 아주 느린 업데이트 (100~1000 step)
        # 빠른 업데이트는 Grid Engine이 드리프트를 "따라가게" 만듦
        if self.update_counter % self.slow_update_threshold != 0:
            return  # 업데이트 스킵
        
        # ⚠️ 중요: 좌표는 원래 입력값을 직접 사용 (정규화로 인한 손실 방지)
        x = current_state[0]  # 직접 저장
        y = current_state[1]  # 직접 저장
        z = current_state[2]  # 직접 저장
        theta_a = current_state[3]  # 직접 저장
        theta_b = current_state[4]  # 직접 저장
        
        # 현재 상태를 위상으로 변환 (위상 계산용)
        phi_x, phi_y, phi_z, phi_a, phi_b = self.projector.coordinate_to_phase(
            x, y, z, theta_a, theta_b
        )
        
        # 위상 정규화
        from ...common.coupling import normalize_phase
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        phi_z = normalize_phase(phi_z, self.config.phase_wrap)
        phi_a = normalize_phase(phi_a, self.config.phase_wrap)
        phi_b = normalize_phase(phi_b, self.config.phase_wrap)
        
        # 상태 업데이트 (속도/가속도는 0으로 유지, 위치/각도는 원래 입력값 직접 저장)
        self.state = Grid5DState(
            phi_x=phi_x, phi_y=phi_y, phi_z=phi_z, phi_a=phi_a, phi_b=phi_b,
            x=x, y=y, z=z,  # 원래 좌표 직접 저장
            theta_a=theta_a, theta_b=theta_b,  # 원래 각도 직접 저장
            v_x=self.state.v_x, v_y=self.state.v_y, v_z=self.state.v_z,
            v_a=self.state.v_a, v_b=self.state.v_b,
            a_x=self.state.a_x, a_y=self.state.a_y, a_z=self.state.a_z,
            alpha_a=self.state.alpha_a, alpha_b=self.state.alpha_b,
            t_ms=self.state.t_ms
        )
        
        # ✅ 핵심: 누적 편향 학습 (Persistent Bias Estimation)
        if self.stable_state is not None:
            # 현재 상태에서 목표 상태와의 차이 계산
            current_array = np.array([x, y, z, theta_a, theta_b])
            target_array = np.array([
                self.stable_state.x,
                self.stable_state.y,
                self.stable_state.z,
                self.stable_state.theta_a,
                self.stable_state.theta_b
            ])
            
            # 편향 = 현재 상태 - (목표 상태 + 기존 편향 추정)
            # 이 편향은 장기적인 드리프트를 나타냄
            expected_state = target_array + self.bias_estimate
            drift = current_array - expected_state
            
            # ✅ Online Phase: Replay Buffer에 기록만 (bias 업데이트 금지) ✨ NEW
            # ⚠️ 중요: Place/Context bias 업데이트는 Replay phase에서만 수행 ✨ NEW
            if self.use_place_cells and self.replay_enabled:
                # 현재 위상 벡터 추출
                phase_vector = self.get_phase_vector()
                
                # Place ID 할당
                place_id = self.place_manager.get_place_id(phase_vector)
                
                # Context ID 할당 (Context Binder 사용 시)
                context_id = None
                if self.use_context_binder:
                    context_id = self.context_binder.get_context_id(self.external_state)
                
                # 현재 속도 및 가속도 계산
                current_velocity = np.array([
                    self.state.v_x, self.state.v_y, self.state.v_z,
                    self.state.v_a, self.state.v_b
                ])
                current_acceleration = np.array([
                    self.state.a_x, self.state.a_y, self.state.a_z,
                    self.state.alpha_a, self.state.alpha_b
                ])
                
                # 오차 계산
                error = drift
                
                # ✅ Replay Buffer에 기록만 (bias 업데이트 금지) ✨ NEW
                self.replay_buffer.add_point(
                    timestamp=self.state.t_ms,
                    phase_vector=phase_vector,
                    current_state=current_array,
                    target_state=target_array,
                    error=error,
                    velocity=current_velocity,
                    acceleration=current_acceleration,
                    place_id=place_id,
                    context_id=context_id
                )
                # ⚠️ Online phase에서는 bias 업데이트 안 함 (Replay phase에서만 수행)
            else:
                # Place Cells를 사용하지 않는 경우: 전역 bias만 업데이트
                self.bias_estimate += self.bias_learning_rate * drift
            
            # 전역 bias는 계속 업데이트 (Persistent Bias Estimator)
            # Place Cells 사용 시에도 전역 bias는 업데이트 (하위 호환성)
            if not (self.use_place_cells and self.replay_enabled):
                self.bias_estimate += self.bias_learning_rate * drift
                # 기존 방식: 전역 bias만 업데이트
                self.bias_estimate += self.bias_learning_rate * drift
            
            # 편향 추정 제한 (발산 방지)
            max_bias = 0.1  # 최대 편향 제한 [m, m, m, deg, deg]
            self.bias_estimate = np.clip(self.bias_estimate, -max_bias, max_bias)
            
            # ✅ Replay Phase: 휴지기에 안정적인 구간만 재생하여 학습 ✨ NEW
            if self.use_replay_consolidation and self.use_place_cells and self.replay_enabled:
                current_time_ms = self.state.t_ms
                current_time_s = current_time_ms / 1000.0  # ms → s 변환
                
                # 휴지기 감지
                if self.replay_consolidation.should_replay(
                    self.last_update_time_for_replay / 1000.0,
                    current_time_s
                ):
                    # ✅ Replay Buffer에서 안정적인 구간만 추출 ✨ NEW
                    stable_segments = self.replay_buffer.get_stable_segments(
                        velocity_threshold=0.01,
                        acceleration_threshold=0.001,
                        min_segment_length=5
                    )
                    
                    # ✅ DEBUG: Replay 시작 로그 ✨ NEW
                    print(f"[REPLAY] 시작 | segments={len(stable_segments)}, buffer_size={len(self.replay_buffer.buffer)}")
                    
                    # ✅ 안정적인 구간만 재생하여 Place/Context bias 업데이트 ✨ NEW
                    consolidated_count = 0
                    total_places_updated = 0
                    total_bias_norm = 0.0
                    
                    for segment in stable_segments:
                        # 각 구간의 Place별로 그룹화
                        place_groups: Dict[Any, List[TrajectoryPoint]] = {}
                        for point in segment:
                            key = point.place_id if point.context_id is None else (point.place_id, point.context_id)
                            if key not in place_groups:
                                place_groups[key] = []
                            place_groups[key].append(point)
                        
                        # 각 Place (및 Context)별로 bias 계산 및 업데이트
                        for key, points in place_groups.items():
                            if len(points) < 3:  # 최소 3개 포인트 필요
                                continue
                            
                            # 구간의 평균 오차 계산 (안정적인 구간의 진짜 편향)
                            errors = np.array([p.error for p in points])
                            mean_error = np.mean(errors, axis=0)
                            mean_error_norm = np.linalg.norm(mean_error)
                            
                            # Place ID 및 Context ID 추출
                            if isinstance(key, tuple):
                                place_id, context_id = key
                            else:
                                place_id = key
                                context_id = None
                            
                            # ✅ Replay phase에서만 Place/Context bias 업데이트 ✨ NEW
                            if self.use_context_binder and context_id is not None:
                                # Place + Context 조합으로 bias 업데이트
                                self.context_binder.update_context_memory(
                                    place_id=place_id,
                                    context_id=context_id,
                                    bias=mean_error,
                                    current_time=current_time_s * 1000.0,  # ms로 변환
                                    learning_rate=self.bias_learning_rate
                                )
                            
                            # Place Memory 업데이트
                            phase_vector = points[0].phase_vector  # 첫 포인트의 위상 사용
                            place_memory = self.place_manager.get_place_memory(place_id)
                            
                            # ✅ 중요: place_center 설정 (블렌딩을 위해 필수) ✨ FIXED
                            if place_memory.place_center is None:
                                place_memory.place_center = phase_vector.copy()
                            else:
                                # Place Field 중심 업데이트 (EMA)
                                place_memory.update_place_center(phase_vector, learning_rate=0.05)
                            
                            # Bias 업데이트
                            bias_before = place_memory.bias_estimate.copy()
                            place_memory.update_bias(
                                new_bias=mean_error,
                                learning_rate=self.bias_learning_rate
                            )
                            bias_after = place_memory.bias_estimate.copy()
                            place_memory.add_bias_to_history(mean_error)
                            place_memory.last_update_time = current_time_s
                            
                            total_places_updated += 1
                            total_bias_norm += np.linalg.norm(bias_after)
                            
                            # ✅ DEBUG: Place 업데이트 로그 ✨ NEW
                            if total_places_updated <= 5:  # 처음 5개만 상세 로그
                                bias_history_len = len(place_memory.bias_history)
                                print(f"[REPLAY] Place {place_id} | bias_norm: {np.linalg.norm(bias_before):.6f} -> {np.linalg.norm(bias_after):.6f} | mean_error_norm: {mean_error_norm:.6f} | visit_count: {place_memory.visit_count} | bias_history_len: {bias_history_len}")
                            
                            # Consolidation 수행
                            if self.replay_consolidation.consolidate_place_memory(place_memory, current_time_s):
                                consolidated_count += 1
                    
                    # ✅ DEBUG: Replay 종료 로그 ✨ NEW
                    print(f"[REPLAY] 종료 | places_updated={total_places_updated}, consolidated={consolidated_count}, avg_bias_norm={total_bias_norm/max(1, total_places_updated):.6f}")
                
                # 마지막 업데이트 시간 기록
                self.last_update_time_for_replay = current_time_ms
        else:
            # 첫 업데이트: 현재 상태를 안정 상태로 저장
            self.stable_state = Grid5DState(
                phi_x=phi_x, phi_y=phi_y, phi_z=phi_z, phi_a=phi_a, phi_b=phi_b,
                x=x, y=y, z=z,
                theta_a=theta_a, theta_b=theta_b,
                v_x=0.0, v_y=0.0, v_z=0.0,
                v_a=0.0, v_b=0.0,
                a_x=0.0, a_y=0.0, a_z=0.0,
                alpha_a=0.0, alpha_b=0.0,
                t_ms=self.state.t_ms
            )
            # 편향 추정 초기화
            self.bias_estimate = np.zeros(5)
    
    def set_target(self, target_state: np.ndarray) -> None:
        """
        목표 상태 설정 (Persistent Bias Estimator용)
        
        Grid Engine이 목표 상태를 안정 상태로 기억하도록 설정합니다.
        편향 추정은 이 목표 상태를 기준으로 수행됩니다.
        
        Args:
            target_state: 목표 상태 [x, y, z, theta_a, theta_b]
                - x, y, z: 위치 [m]
                - theta_a, theta_b: 각도 [deg]
        
        Author: GNJz
        Created: 2026-01-20
        Updated: 2026-01-20 (Persistent Bias Estimator로 재정의)
        Made in GNJz
        """
        # 목표 상태를 위상으로 변환 (정규화 전)
        phi_x, phi_y, phi_z, phi_a, phi_b = self.projector.coordinate_to_phase(
            target_state[0],  # x [m]
            target_state[1],  # y [m]
            target_state[2],  # z [m]
            target_state[3],  # theta_a [deg]
            target_state[4]   # theta_b [deg]
        )
        
        # 위상 정규화
        from ...common.coupling import normalize_phase
        phi_x_norm = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y_norm = normalize_phase(phi_y, self.config.phase_wrap)
        phi_z_norm = normalize_phase(phi_z, self.config.phase_wrap)
        phi_a_norm = normalize_phase(phi_a, self.config.phase_wrap)
        phi_b_norm = normalize_phase(phi_b, self.config.phase_wrap)
        
        # ⚠️ 중요: 좌표는 원래 입력값을 직접 사용 (정규화로 인한 손실 방지)
        # normalize_phase()가 2π를 0으로 정규화하면 좌표가 손실됨
        x = target_state[0]  # 직접 저장
        y = target_state[1]  # 직접 저장
        z = target_state[2]  # 직접 저장
        theta_a = target_state[3]  # 직접 저장
        theta_b = target_state[4]  # 직접 저장
        
        # 목표 상태를 안정 상태로 설정
        self.stable_state = Grid5DState(
            phi_x=phi_x_norm, phi_y=phi_y_norm, phi_z=phi_z_norm, 
            phi_a=phi_a_norm, phi_b=phi_b_norm,
            x=x, y=y, z=z,  # 원래 좌표 직접 저장
            theta_a=theta_a, theta_b=theta_b,  # 원래 각도 직접 저장
            v_x=0.0, v_y=0.0, v_z=0.0,
            v_a=0.0, v_b=0.0,
            a_x=0.0, a_y=0.0, a_z=0.0,
            alpha_a=0.0, alpha_b=0.0,
            t_ms=self.state.t_ms
        )
        
        # 편향 추정 초기화 (목표 변경 시 편향도 리셋)
        self.bias_estimate = np.zeros(5)
        self.update_counter = 0
    
    def provide_reference(
        self,
        current_state: np.ndarray = None,
        target_state: np.ndarray = None,
        velocity: np.ndarray = None,
        acceleration: np.ndarray = None
    ) -> np.ndarray:
        """
        Reference Correction 제공 (Persistent Bias Estimator + Cerebellum)
        
        해마 메모리의 학습된 편향과 소뇌 엔진의 즉각 보정을 결합하여 Reference Correction을 제공합니다.
        
        핵심 구조:
        - 해마: 장기 기억 기반 보정 (느림, 분~시간~일)
        - 소뇌: 즉각 보정 (빠름, ms)
        - 결합: reference = hippocampus_correction + cerebellum_correction
        
        Args:
            current_state: 현재 상태 [x, y, z, theta_a, theta_b] (선택적)
            target_state: 목표 상태 [x, y, z, theta_a, theta_b] (소뇌용)
            velocity: 현재 속도 [v_x, v_y, v_z, v_a, v_b] (소뇌용)
            acceleration: 현재 가속도 [a_x, a_y, a_z, alpha_a, alpha_b] (소뇌용)
        
        Returns:
            reference_correction: Reference Correction [x, y, z, theta_a, theta_b]
                - 해마 보정 + 소뇌 보정
        
        Author: GNJz
        Created: 2026-01-20
        Updated: 2026-01-20 (Hippocampus + Cerebellum 통합)
        Made in GNJz
        """
        if self.stable_state is None:
            # 안정 상태가 없으면 0 반환
            return np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        
        # 1. 해마 메모리 보정 (장기 기억 기반)
        hippocampus_correction = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        
        # ✅ Place Cells 사용 시: Place별 bias 반환 ✨ NEW
        if self.use_place_cells:
            # 현재 위상 벡터 추출
            phase_vector = self.get_phase_vector()
            
            # Place ID 할당
            place_id = self.place_manager.get_place_id(phase_vector)
            
            # ✅ Context Binder 사용 시: Place + Context 조합으로 bias 반환 ✨ NEW
            if self.use_context_binder:
                # Context ID 할당
                context_id = self.context_binder.get_context_id(self.external_state)
                
                # Place + Context 조합의 bias 추정값 반환
                context_bias = self.context_binder.get_bias_estimate(place_id, context_id)
                reference_correction = -context_bias
            else:
                # Place만 사용 (Context 없음)
                # ✅ Place Blending 사용 (Soft-Switching) ✨ NEW
                place_bias = self.place_manager.get_bias_estimate(
                    phase_vector,
                    use_blending=True,  # Soft-Switching 활성화
                    top_k=5,  # 상위 5개 Place Cell 사용
                    sigma=0.5  # 가우시안 표준 편차
                )
                reference_correction = -place_bias
                
                # ✅ DEBUG: provide_reference 로그 (처음 몇 번만) ✨ NEW
                if not hasattr(self, '_debug_ref_count'):
                    self._debug_ref_count = 0
                self._debug_ref_count += 1
                if self._debug_ref_count <= 3:
                    place_memory = self.place_manager.get_place_memory(place_id)
                    print(f"[REF] place_id={place_id}, bias_norm={np.linalg.norm(place_bias):.6f}, corr_norm={np.linalg.norm(reference_correction):.6f}, visit_count={place_memory.visit_count}, place_center={place_memory.place_center is not None}")
        else:
            # 기존 방식: 전역 bias 반환
            hippocampus_correction = -self.bias_estimate
        
        # 2. 소뇌 엔진 보정 (즉각 보정) ✨ NEW
        cerebellum_correction = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        
        if self.use_cerebellum and target_state is not None:
            # 현재 상태가 없으면 현재 출력 상태 사용
            if current_state is None:
                current_state = np.array([
                    self.state.x,
                    self.state.y,
                    self.state.z,
                    self.state.theta_a,
                    self.state.theta_b
                ])
            
            # 속도/가속도가 없으면 현재 상태에서 계산
            if velocity is None:
                velocity = np.array([
                    self.state.v_x,
                    self.state.v_y,
                    self.state.v_z,
                    self.state.v_a,
                    self.state.v_b
                ])
            
            if acceleration is None:
                acceleration = np.array([
                    self.state.a_x,
                    self.state.a_y,
                    self.state.a_z,
                    self.state.alpha_a,
                    self.state.alpha_b
                ])
            
            # 소뇌 보정값 계산
            cerebellum_correction = self.cerebellum.compute_correction(
                current_state=current_state,
                target_state=target_state,
                velocity=velocity,
                acceleration=acceleration,
                context=self.external_state,
                dt=self.config.dt_ms / 1000.0  # ms → s 변환
            )
        
        # 3. 통합 보정 (해마 + 소뇌)
        reference_correction = hippocampus_correction + cerebellum_correction
        
        return reference_correction
    
    def set_external_state(self, external_state: Dict[str, Any]) -> None:
        """
        외부 상태 설정 (Context Binder용)
        
        외부 상태 예시:
        - tool_type: 공구 타입 (예: "tool_A", "tool_B")
        - temperature: 온도 (예: 20.0, 25.0)
        - step_number: 작업 단계 (예: 0, 1, 2)
        - material: 재료 타입 (예: "aluminum", "steel")
        
        Args:
            external_state: 외부 상태 딕셔너리
        """
        self.external_state = external_state.copy()


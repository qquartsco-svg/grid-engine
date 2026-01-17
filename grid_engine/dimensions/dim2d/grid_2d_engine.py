"""
Grid Engine
Ring ⊗ Ring 조립 + step()만 담당

이 모듈은 2D Grid Engine의 메인 엔진입니다.
Ring Attractor Engine 2개(X, Y)를 직교 결합하여 2D 위상 공간을 구성합니다.

뉴턴 제2법칙과의 연관성:
    Grid Engine은 뉴턴 제2법칙 (F = ma)을 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    
    물리적 대응 관계:
        물리량          Grid Engine          단위
        위치 r          위상 φ (phase)       [rad]
        속도 v          속도 입력 (velocity)  [m/s]
        가속도 a        가속도 입력 (accel)   [m/s²]
        힘 F            외란 (disturbance)    [N]
    
    상태 방정식 (뉴턴 역학의 이산화):
        dφx/dt = vx(t)
        dφy/dt = vy(t)
        dvx/dt = ax(t)  ← 뉴턴 2법칙
        dvy/dt = ay(t)  ← 뉴턴 2법칙
    
    코드 구현:
        integrator.semi_implicit_euler()에서 뉴턴 2법칙을 적용
        v_new = v_old + a * dt_s  ← 속도 업데이트 (F = ma)
        phi_new = phi_old + v * dt_s + 0.5 * a * dt_s²  ← 위치(위상) 업데이트 (경로 통합)
    
    상세 설명: docs/NEWTONS_LAW_CONNECTION.md 참조

핵심 아키텍처:
    Grid Engine = Ring X ⊗ Ring Y
    - Ring X: X 방향 위상 관리 (φx ∈ [0, 2π))
    - Ring Y: Y 방향 위상 관리 (φy ∈ [0, 2π))
    - 직교 결합: 각 Ring은 독립적으로 동작

모듈 분리 원칙:
    - grid_engine.py: 조립 + step()만 담당
    - integrator.py: 수치 적분 (경로 통합, 뉴턴 2법칙)
    - coupling.py: 위상 정규화 및 변환
    - projector.py: 좌표 투영 (관측자)
    - energy.py: 에너지 계산 및 진단
    - adapters/ring_adapter.py: Ring Engine 래핑

알고리즘 흐름:
    1. 수치 적분: 속도/가속도 → 위상 업데이트 (뉴턴 2법칙)
    2. Ring 안정화: 위상을 Attractor에 붙잡기
    3. 좌표 투영: 위상 → 좌표 변환 (projector 사용)

수학적 배경:
    Grid Engine은 연속 어트랙터 네트워크(Continuous Attractor Network)의
    2차원 확장입니다. 경로 통합(Path Integration)을 통해 위치 상태를 유지합니다.
    
    위상 공간: T² = S¹ × S¹ (토러스)
    상태 방정식: dφ/dt = v + ½a·t

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from typing import Optional
from .config_2d import GridEngineConfig
from .types_2d import GridState, GridInput, GridOutput, GridDiagnostics
from .integrator_2d import semi_implicit_euler
from ...common.coupling import update_state_from_phases, normalize_phase
from ...common.energy import compute_diagnostics, calculate_energy
from ...common.adapters.ring_adapter import RingAdapter, RingAdapterConfig
from .projector_2d import CoordinateProjector


class GridEngine:
    """
    Grid Engine
    
    Ring ⊗ Ring 구조로 2D 위치 상태 유지
    """
    
    def __init__(
        self,
        config: Optional[GridEngineConfig] = None,
        initial_x: float = 0.0,
        initial_y: float = 0.0
    ):
        """
        Grid Engine 초기화
        
        Args:
            config: 설정 (None이면 기본값)
            initial_x: 초기 X 좌표
            initial_y: 초기 Y 좌표
        """
        self.config = config or GridEngineConfig()
        self.config.validate()
        
        # Ring Adapter 생성
        ring_cfg_x = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_x
        )
        ring_cfg_y = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_y
        )
        self.ring_adapter = RingAdapter(ring_cfg_x, ring_cfg_y)
        
        # Coordinate Projector 생성 (좌표 투영 담당)
        self.projector = CoordinateProjector(self.config)
        
        # 초기 상태 설정
        # 주의: Grid Engine은 위상만 유지, 좌표는 projector가 계산
        phi_x, phi_y = self.projector.coordinate_to_phase(initial_x, initial_y)
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        
        self.state = GridState(
            phi_x=phi_x,
            phi_y=phi_y,
            x=initial_x,  # 초기값 저장 (나중에는 projector로 계산)
            y=initial_y,  # 초기값 저장 (나중에는 projector로 계산)
            v_x=0.0,
            v_y=0.0,
            a_x=0.0,
            a_y=0.0,
            t_ms=0.0
        )
        
        self.state_prev: Optional[GridState] = None
    
    def step(self, inp: GridInput) -> GridOutput:
        """
        Grid Engine step 함수
        
        한 스텝 실행: 경로 통합 → Ring 안정화 → 좌표 투영
        
        알고리즘 흐름:
            1. 수치 적분: 속도/가속도 → 위상 업데이트
               수식: φ(t+Δt) = φ(t) + v·Δt + ½a·Δt²
            
            2. Ring 안정화: 위상을 Attractor에 붙잡기
               Ring Attractor가 위상을 끌어당겨 노이즈/외란 억제
            
            3. 좌표 투영: 위상 → 좌표 변환 (projector 사용)
               수식: x = φx · (Lx / 2π)
        
        수학적 배경:
            경로 통합(Path Integration): 
                속도 v와 가속도 a로부터 위치(위상)를 적분합니다.
                뉴턴 2법칙(F = ma)을 기반으로 합니다.
            
            Attractor 동역학:
                Ring Attractor는 위상을 안정적인 manifold로 끌어당깁니다.
                노이즈와 외란에 강건한 특성을 제공합니다.
            
            좌표 투영:
                내부 위상 φ ∈ [0, 2π)를 외부 좌표 x ∈ [0, L)로 변환합니다.
                관측자 패턴(Observer Pattern)을 따릅니다.
        
        Args:
            inp: 입력 데이터
                - v_x, v_y: 속도 [m/s]
                - a_x, a_y: 가속도 [m/s²] (선택적)
        
        Returns:
            출력 데이터
                - x, y: 좌표 [m] (projector가 계산)
                - phi_x, phi_y: 위상 [rad] (내부 상태)
        
        Author: [작성자 시그니처]
        Created: 2026-01
        """
        # ============================================================
        # 0. 이전 상태 저장 (진단용)
        # ============================================================
        # 진단 모드가 활성화된 경우, 이전 상태를 저장하여
        # 에너지 변화, 안정성 등을 계산할 수 있도록 합니다.
        if self.config.diagnostics_enabled:
            self.state_prev = GridState(
                phi_x=self.state.phi_x,
                phi_y=self.state.phi_y,
                x=self.state.x,
                y=self.state.y,
                v_x=self.state.v_x,
                v_y=self.state.v_y,
                a_x=self.state.a_x,
                a_y=self.state.a_y,
                t_ms=self.state.t_ms
            )
        
        # ============================================================
        # 1. 수치 적분 (Semi-implicit Euler)
        # ============================================================
        # 경로 통합(Path Integration): 속도와 가속도로부터 위상 업데이트
        #
        # 수식:
        #   v(t+Δt) = v(t) + a·Δt          [속도 업데이트]
        #   φ(t+Δt) = φ(t) + v·Δt + ½a·Δt²  [위상 업데이트]
        #
        # 물리 단위:
        #   - 입력: v [m/s], a [m/s²], dt_ms [ms]
        #   - 변환: dt_s = dt_ms / 1000.0 [s]
        #   - 수식: dφ = v [m/s] * dt_s [s] + ½a [m/s²] * (dt_s [s])²
        #
        # 참고: integrator.py에서 물리 법칙 적용을 위해
        #       ms를 s로 변환하여 단위 일관성을 확보합니다.
        new_phi_x, new_phi_y, new_v_x, new_v_y = semi_implicit_euler(
            self.state,
            inp,
            self.config.dt_ms,
            self.config.tau_ms
        )
        
        # ============================================================
        # 2. Ring 안정화 (Attractor 동역학)
        # ============================================================
        # Ring Attractor가 위상을 안정적인 manifold로 끌어당깁니다.
        #
        # 동작 원리:
        #   1. 위상을 Ring 인덱스로 변환
        #      idx = (φ / 2π) * ring_size
        #
        #   2. Ring에 위상 주입
        #      ring.inject(direction_idx=idx, strength=0.8)
        #
        #   3. Ring 동역학 실행 (안정화)
        #      ring.run(duration_ms=dt_ms)
        #
        #   4. 안정화된 위상 추출
        #      φ_stabilized = (ring.center / ring_size) * 2π
        #
        # 효과:
        #   - 노이즈 억제: 위상이 Attractor에 붙잡혀 노이즈가 감쇠됩니다
        #   - 외란 저항성: 외부 외란이 있어도 위상이 안정적으로 유지됩니다
        #   - 가중 평균: 원래 위상 90% + Ring 조정 10%
        stabilized_phi_x, stabilized_phi_y, energy_x, energy_y = \
            self.ring_adapter.step(new_phi_x, new_phi_y, self.config.dt_ms)
        
        # ============================================================
        # 3. 상태 업데이트 (위상 정규화 및 좌표 투영)
        # ============================================================
        # 위상 정규화: 주기적 경계 조건 적용
        #
        # 수식: φ_norm = φ mod 2π ∈ [0, 2π)
        #
        # 의미: 위상이 주기적 경계 조건을 만족하도록 [0, 2π) 범위로 감쌉니다.
        #       토러스(Torus) 공간의 특성상 위상은 주기적입니다.
        #
        # 주의: Grid Engine은 내부 위상(φ)만 관리합니다.
        #       좌표(x, y)는 projector(관측자)가 계산합니다.
        phi_x_norm = normalize_phase(stabilized_phi_x, self.config.phase_wrap)
        phi_y_norm = normalize_phase(stabilized_phi_y, self.config.phase_wrap)
        
        # 좌표 투영: 위상 → 좌표 변환 (관측자 책임)
        #
        # 수식: x = φx · (Lx / 2π)
        #       y = φy · (Ly / 2π)
        #
        # 의미: 내부 위상 φ ∈ [0, 2π)를 외부 좌표 x ∈ [0, L)로 변환합니다.
        #       이는 관측자 패턴(Observer Pattern)을 따릅니다.
        #
        # 책임 분리:
        #   - Grid Engine: 위상 상태만 유지
        #   - CoordinateProjector: 좌표 계산 (관측자)
        x, y = self.projector.phase_to_coordinate(phi_x_norm, phi_y_norm)
        
        # 상태 업데이트 (좌표는 projector가 계산한 값으로)
        self.state = GridState(
            phi_x=phi_x_norm,
            phi_y=phi_y_norm,
            x=x,  # projector가 계산한 좌표
            y=y,  # projector가 계산한 좌표
            v_x=new_v_x,
            v_y=new_v_y,
            a_x=inp.a_x if inp.a_x is not None else self.state.a_x,
            a_y=inp.a_y if inp.a_y is not None else self.state.a_y,
            t_ms=self.state.t_ms + self.config.dt_ms
        )
        
        # 4. 출력 생성
        # 출력도 projector를 통해 좌표 계산 (일관성 유지)
        output_x, output_y = self.projector.phase_to_coordinate(
            self.state.phi_x, self.state.phi_y
        )
        
        output = GridOutput(
            x=output_x,
            y=output_y,
            phi_x=self.state.phi_x,
            phi_y=self.state.phi_y
        )
        
        # 진단 정보 추가 (선택적)
        if self.config.diagnostics_enabled and self.state_prev is not None:
            diagnostics = compute_diagnostics(
                self.state,
                self.state_prev,
                self.config,
                energy_x,
                energy_y
            )
            output.stability_score = diagnostics.stability_score
            output.energy = diagnostics.energy
        
        # 에너지 감소 검증
        if self.config.energy_check_enabled and self.state_prev is not None:
            energy_prev = calculate_energy(self.state_prev, self.config, energy_x, energy_y)
            energy_curr = calculate_energy(self.state, self.config, energy_x, energy_y)
            if energy_curr > energy_prev:
                # 경고 (에너지 증가)
                pass  # 로깅 또는 예외 처리
        
        return output
    
    def get_state(self) -> GridState:
        """현재 상태 반환"""
        return self.state
    
    def reset(self, x: float = 0.0, y: float = 0.0):
        """
        상태 리셋
        
        Args:
            x: 초기 X 좌표 [m]
            y: 초기 Y 좌표 [m]
        """
        # 좌표 → 위상 변환 (projector 사용)
        phi_x, phi_y = self.projector.coordinate_to_phase(x, y)
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        
        self.state = GridState(
            phi_x=phi_x,
            phi_y=phi_y,
            x=x,
            y=y,
            v_x=0.0,
            v_y=0.0,
            a_x=0.0,
            a_y=0.0,
            t_ms=0.0
        )
        self.ring_adapter.reset()


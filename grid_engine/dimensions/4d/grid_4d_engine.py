"""
Grid 4D Engine
Ring ⊗ Ring ⊗ Ring ⊗ Ring 조립 + step()만 담당

이 모듈은 4D Grid Engine의 메인 엔진입니다.
Ring Attractor Engine 4개(X, Y, Z, W)를 직교 결합하여 4D 위상 공간을 구성합니다.

4D 확장:
    - 2D: Grid = Ring X ⊗ Ring Y
    - 3D: Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z
    - 4D: Grid 4D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W ✨ NEW

뉴턴 제2법칙과의 연관성 (4D):
    Grid 4D Engine은 뉴턴 제2법칙 (F = ma)을 4차원 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    
    물리적 대응 관계 (4D):
        물리량          Grid 4D Engine          단위
        위치 r          위상 φ (phase)           [rad]
        속도 v          속도 입력 (velocity)     [m/s]
        가속도 a        가속도 입력 (accel)      [m/s²]
        힘 F            외란 (disturbance)      [N]
    
    상태 방정식 (뉴턴 역학의 이산화, 4D):
        dφx/dt = vx(t)
        dφy/dt = vy(t)
        dφz/dt = vz(t)
        dφw/dt = vw(t)  ← W 방향 추가 ✨ NEW
        
        dvx/dt = ax(t)  ← 뉴턴 2법칙
        dvy/dt = ay(t)  ← 뉴턴 2법칙
        dvz/dt = az(t)  ← 뉴턴 2법칙
        dvw/dt = aw(t)  ← 뉴턴 2법칙 (W 방향 추가) ✨ NEW
    
    코드 구현:
        integrator_4d.semi_implicit_euler_4d()에서 뉴턴 2법칙을 적용
        v_new = v_old + a * dt_s  ← 속도 업데이트 (F = ma)
        phi_new = phi_old + v * dt_s + 0.5 * a * dt_s²  ← 위치(위상) 업데이트 (경로 통합)
    
    상세 설명:
        - docs/NEWTONS_LAW_CONNECTION.md (뉴턴 2법칙)
        - docs/4D_CONCEPT_AND_EQUATIONS.md (4D 개념 및 수식)

핵심 아키텍처:
    Grid 4D Engine = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W
    - Ring X: X 방향 위상 관리 (φx ∈ [0, 2π))
    - Ring Y: Y 방향 위상 관리 (φy ∈ [0, 2π))
    - Ring Z: Z 방향 위상 관리 (φz ∈ [0, 2π))
    - Ring W: W 방향 위상 관리 (φw ∈ [0, 2π)) ✨ NEW
    - 직교 결합: 각 Ring은 독립적으로 동작

모듈 분리 원칙:
    - grid_4d_engine.py: 조립 + step()만 담당
    - integrator_4d.py: 수치 적분 (경로 통합, 뉴턴 2법칙, 4D)
    - coupling.py: 위상 정규화 (2D/3D/4D 공통 사용 가능)
    - projector_4d.py: 좌표 투영 (관측자, 4D)
    - energy.py: 에너지 계산 및 진단 (2D만 지원, 4D는 TODO)
    - adapters/ring_4d_adapter.py: Ring Engine 래핑 (4D)

알고리즘 흐름:
    1. 수치 적분: 속도/가속도 → 위상 업데이트 (뉴턴 2법칙, 4D)
    2. Ring 안정화: 위상을 Attractor에 붙잡기 (4개 Ring)
    3. 좌표 투영: 위상 → 4D 좌표 변환 (projector_4d 사용)

수학적 배경:
    Grid 4D Engine은 연속 어트랙터 네트워크(Continuous Attractor Network)의
    4차원 확장입니다. 경로 통합(Path Integration)을 통해 4D 위치 상태를 유지합니다.
    
    위상 공간: T⁴ = S¹ × S¹ × S¹ × S¹ (토러스, 4차원)
    상태 방정식: dΦ/dt = v + ½a·t (4D 벡터)

상세 설명:
    - docs/4D_CONCEPT_AND_EQUATIONS.md (4D 개념 및 수식)
    - docs/RING_ATTRACTOR_RELATIONSHIP.md (Ring Attractor 연관성)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

from typing import Optional
from .config_4d import Grid4DConfig
from .types_4d import Grid4DState, Grid4DInput, Grid4DOutput, Grid4DDiagnostics
from .integrator_4d import semi_implicit_euler_4d
from ...common.coupling import normalize_phase
from ...common.energy import compute_diagnostics, calculate_energy
from ...common.adapters.ring_4d_adapter import Ring4DAdapter
from ...common.adapters.ring_adapter import RingAdapterConfig
from .projector_4d import Coordinate4DProjector


class Grid4DEngine:
    """
    Grid 4D Engine
    
    Ring ⊗ Ring ⊗ Ring ⊗ Ring 구조로 4D 위치 상태 유지
    
    4D 확장:
        - 2D: Ring X ⊗ Ring Y → (x, y)
        - 3D: Ring X ⊗ Ring Y ⊗ Ring Z → (x, y, z)
        - 4D: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W → (x, y, z, w) ✨ NEW
    """
    
    def __init__(
        self,
        config: Optional[Grid4DConfig] = None,
        initial_x: float = 0.0,
        initial_y: float = 0.0,
        initial_z: float = 0.0,
        initial_w: float = 0.0
    ):
        """
        Grid 4D Engine 초기화
        
        Args:
            config: 설정 (None이면 기본값)
            initial_x: 초기 X 좌표 [m]
            initial_y: 초기 Y 좌표 [m]
            initial_z: 초기 Z 좌표 [m]
            initial_w: 초기 W 좌표 [m] (새로 추가) ✨ NEW
        """
        self.config = config or Grid4DConfig()
        self.config.validate()
        
        # Ring 4D Adapter 생성
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
        ring_cfg_w = RingAdapterConfig(
            size=self.config.ring_size,
            config=self.config.ring_cfg_w
        )  # W 방향 추가 ✨ NEW
        self.ring_adapter = Ring4DAdapter(ring_cfg_x, ring_cfg_y, ring_cfg_z, ring_cfg_w)
        
        # Coordinate 4D Projector 생성 (좌표 투영 담당)
        self.projector = Coordinate4DProjector(self.config)
        
        # 초기 상태 설정 (4D)
        # 주의: Grid 4D Engine은 위상만 유지, 좌표는 projector가 계산
        phi_x, phi_y, phi_z, phi_w = self.projector.coordinate_to_phase(
            initial_x, initial_y, initial_z, initial_w
        )
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        phi_z = normalize_phase(phi_z, self.config.phase_wrap)
        phi_w = normalize_phase(phi_w, self.config.phase_wrap)  # W 방향 추가 ✨ NEW
        
        self.state = Grid4DState(
            phi_x=phi_x,
            phi_y=phi_y,
            phi_z=phi_z,
            phi_w=phi_w,  # W 위상 추가 ✨ NEW
            x=initial_x,  # 초기값 저장 (나중에는 projector로 계산)
            y=initial_y,  # 초기값 저장 (나중에는 projector로 계산)
            z=initial_z,  # 초기값 저장 (나중에는 projector로 계산)
            w=initial_w,  # 초기값 저장 (나중에는 projector로 계산) (W 방향 추가) ✨ NEW
            v_x=0.0,
            v_y=0.0,
            v_z=0.0,
            v_w=0.0,  # W 속도 추가 ✨ NEW
            a_x=0.0,
            a_y=0.0,
            a_z=0.0,
            a_w=0.0,  # W 가속도 추가 ✨ NEW
            t_ms=0.0
        )
        
        self.state_prev: Optional[Grid4DState] = None
    
    def step(self, inp: Grid4DInput) -> Grid4DOutput:
        """
        Grid 4D Engine step 함수
        
        한 스텝 실행: 4D 경로 통합 → Ring 안정화 (4개) → 4D 좌표 투영
        
        알고리즘 흐름 (4D):
            1. 수치 적분: 속도/가속도 → 위상 업데이트 (4D)
               수식: φ(t+Δt) = φ(t) + v·Δt + ½a·Δt²
            
            2. Ring 안정화: 위상을 Attractor에 붙잡기 (4개 Ring)
               Ring Attractor가 위상을 끌어당겨 노이즈/외란 억제
            
            3. 좌표 투영: 위상 → 4D 좌표 변환 (projector_4d 사용)
               수식: x = φx · (Lx / 2π), y = φy · (Ly / 2π), z = φz · (Lz / 2π), w = φw · (Lw / 2π)
        
        수학적 배경 (4D):
            경로 통합(Path Integration): 
                속도 v = (vx, vy, vz, vw)와 가속도 a = (ax, ay, az, aw)로부터 위치(위상)를 적분합니다.
                뉴턴 2법칙(F = ma)을 기반으로 합니다.
            
            Attractor 동역학:
                Ring Attractor는 위상을 안정적인 manifold로 끌어당깁니다.
                노이즈와 외란에 강건한 특성을 제공합니다.
            
            좌표 투영 (4D):
                내부 위상 φ = (φx, φy, φz, φw) ∈ [0, 2π)⁴를 외부 좌표 (x, y, z, w) ∈ [0, L)⁴로 변환합니다.
                관측자 패턴(Observer Pattern)을 따릅니다.
        
        Args:
            inp: 입력 데이터 (4D)
                - v_x, v_y, v_z, v_w: 속도 [m/s]
                - a_x, a_y, a_z, a_w: 가속도 [m/s²] (선택적)
        
        Returns:
            출력 데이터 (4D)
                - x, y, z, w: 좌표 [m] (projector가 계산)
                - phi_x, phi_y, phi_z, phi_w: 위상 [rad] (내부 상태)
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # ============================================================
        # 0. 이전 상태 저장 (진단용)
        # ============================================================
        # 진단 모드가 활성화된 경우, 이전 상태를 저장하여
        # 에너지 변화, 안정성 등을 계산할 수 있도록 합니다.
        if self.config.diagnostics_enabled:
            self.state_prev = Grid4DState(
                phi_x=self.state.phi_x,
                phi_y=self.state.phi_y,
                phi_z=self.state.phi_z,
                phi_w=self.state.phi_w,  # W 위상 추가 ✨ NEW
                x=self.state.x,
                y=self.state.y,
                z=self.state.z,
                w=self.state.w,  # W 좌표 추가 ✨ NEW
                v_x=self.state.v_x,
                v_y=self.state.v_y,
                v_z=self.state.v_z,
                v_w=self.state.v_w,  # W 속도 추가 ✨ NEW
                a_x=self.state.a_x,
                a_y=self.state.a_y,
                a_z=self.state.a_z,
                a_w=self.state.a_w,  # W 가속도 추가 ✨ NEW
                t_ms=self.state.t_ms
            )
        
        # ============================================================
        # 1. 수치 적분 (Semi-implicit Euler, 4D)
        # ============================================================
        # 경로 통합(Path Integration): 속도와 가속도로부터 위상 업데이트 (4D)
        #
        # 수식 (4D):
        #   v(t+Δt) = v(t) + a·Δt          [속도 업데이트]
        #   φ(t+Δt) = φ(t) + v·Δt + ½a·Δt²  [위상 업데이트]
        #
        # 4D 확장:
        #   - 2D: (vx, vy), (ax, ay) → (φx, φy)
        #   - 3D: (vx, vy, vz), (ax, ay, az) → (φx, φy, φz)
        #   - 4D: (vx, vy, vz, vw), (ax, ay, az, aw) → (φx, φy, φz, φw) ✨ NEW
        #
        # 물리 단위:
        #   - 입력: v [m/s], a [m/s²], dt_ms [ms]
        #   - 변환: dt_s = dt_ms / 1000.0 [s]
        #   - 수식: dφ = v [m/s] * dt_s [s] + ½a [m/s²] * (dt_s [s])²
        #
        # 참고: integrator_4d.py에서 물리 법칙 적용을 위해
        #       ms를 s로 변환하여 단위 일관성을 확보합니다.
        new_phi_x, new_phi_y, new_phi_z, new_phi_w, new_v_x, new_v_y, new_v_z, new_v_w = \
            semi_implicit_euler_4d(
                self.state,
                inp,
                self.config.dt_ms,
                self.config.tau_ms
            )
        
        # ============================================================
        # 2. Ring 안정화 (Attractor 동역학, 4D)
        # ============================================================
        # Ring Attractor가 위상을 안정적인 manifold로 끌어당깁니다 (4개 Ring).
        #
        # 동작 원리 (4D):
        #   1. 위상을 Ring 인덱스로 변환 (4D)
        #      idx_x = (φx / 2π) * ring_size
        #      idx_y = (φy / 2π) * ring_size
        #      idx_z = (φz / 2π) * ring_size
        #      idx_w = (φw / 2π) * ring_size  ← W 방향 추가 ✨ NEW
        #
        #   2. Ring에 위상 주입 (4개 Ring)
        #      ring_x.inject(direction_idx=idx_x, strength=0.8)
        #      ring_y.inject(direction_idx=idx_y, strength=0.8)
        #      ring_z.inject(direction_idx=idx_z, strength=0.8)
        #      ring_w.inject(direction_idx=idx_w, strength=0.8)  ← W 방향 추가 ✨ NEW
        #
        #   3. Ring 동역학 실행 (안정화, 4개 Ring)
        #      ring_x.run(duration_ms=dt_ms)
        #      ring_y.run(duration_ms=dt_ms)
        #      ring_z.run(duration_ms=dt_ms)
        #      ring_w.run(duration_ms=dt_ms)  ← W 방향 추가 ✨ NEW
        #
        #   4. 안정화된 위상 추출 (4D)
        #      φ_stabilized = (ring.center / ring_size) * 2π
        #
        # 효과 (4D):
        #   - 노이즈 억제: 위상이 Attractor에 붙잡혀 노이즈가 감쇠됩니다 (4개 방향)
        #   - 외란 저항성: 외부 외란이 있어도 위상이 안정적으로 유지됩니다 (4개 방향)
        #   - 가중 평균: 원래 위상 90% + Ring 조정 10% (각 방향별)
        stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_w, \
        energy_x, energy_y, energy_z, energy_w = \
            self.ring_adapter.step(new_phi_x, new_phi_y, new_phi_z, new_phi_w, self.config.dt_ms)
        
        # ============================================================
        # 3. 상태 업데이트 (위상 정규화 및 4D 좌표 투영)
        # ============================================================
        # 위상 정규화: 주기적 경계 조건 적용 (4D)
        #
        # 수식: φ_norm = φ mod 2π ∈ [0, 2π)
        #
        # 의미: 위상이 주기적 경계 조건을 만족하도록 [0, 2π) 범위로 감쌉니다.
        #       토러스(Torus) 공간의 특성상 위상은 주기적입니다.
        #
        # 4D 확장:
        #   - 2D: (φx, φy) → (φx_norm, φy_norm)
        #   - 3D: (φx, φy, φz) → (φx_norm, φy_norm, φz_norm)
        #   - 4D: (φx, φy, φz, φw) → (φx_norm, φy_norm, φz_norm, φw_norm) ✨ NEW
        #
        # 주의: Grid 4D Engine은 내부 위상(φx, φy, φz, φw)만 관리합니다.
        #       좌표(x, y, z, w)는 projector(관측자)가 계산합니다.
        phi_x_norm = normalize_phase(stabilized_phi_x, self.config.phase_wrap)
        phi_y_norm = normalize_phase(stabilized_phi_y, self.config.phase_wrap)
        phi_z_norm = normalize_phase(stabilized_phi_z, self.config.phase_wrap)
        phi_w_norm = normalize_phase(stabilized_phi_w, self.config.phase_wrap)  # W 방향 추가 ✨ NEW
        
        # 좌표 투영: 위상 → 4D 좌표 변환 (관측자 책임)
        #
        # 수식 (4D):
        #   x = φx · (Lx / 2π)
        #   y = φy · (Ly / 2π)
        #   z = φz · (Lz / 2π)
        #   w = φw · (Lw / 2π)  ← W 방향 추가 ✨ NEW
        #
        # 의미: 내부 위상 φ ∈ [0, 2π)⁴를 외부 좌표 (x, y, z, w) ∈ [0, L)⁴로 변환합니다.
        #       이는 관측자 패턴(Observer Pattern)을 따릅니다.
        #
        # 책임 분리:
        #   - Grid 4D Engine: 위상 상태만 유지 (φx, φy, φz, φw)
        #   - Coordinate4DProjector: 좌표 계산 (관측자, x, y, z, w)
        x, y, z, w = self.projector.phase_to_coordinate(phi_x_norm, phi_y_norm, phi_z_norm, phi_w_norm)
        
        # 상태 업데이트 (좌표는 projector가 계산한 값으로)
        self.state = Grid4DState(
            phi_x=phi_x_norm,
            phi_y=phi_y_norm,
            phi_z=phi_z_norm,
            phi_w=phi_w_norm,  # W 위상 추가 ✨ NEW
            x=x,  # projector가 계산한 좌표
            y=y,  # projector가 계산한 좌표
            z=z,  # projector가 계산한 좌표
            w=w,  # projector가 계산한 좌표 (W 방향 추가) ✨ NEW
            v_x=new_v_x,
            v_y=new_v_y,
            v_z=new_v_z,
            v_w=new_v_w,  # W 속도 추가 ✨ NEW
            a_x=inp.a_x if inp.a_x is not None else self.state.a_x,
            a_y=inp.a_y if inp.a_y is not None else self.state.a_y,
            a_z=inp.a_z if inp.a_z is not None else self.state.a_z,
            a_w=inp.a_w if inp.a_w is not None else self.state.a_w,  # W 가속도 추가 ✨ NEW
            t_ms=self.state.t_ms + self.config.dt_ms
        )
        
        # 4. 출력 생성 (4D)
        # 출력도 projector를 통해 좌표 계산 (일관성 유지)
        output_x, output_y, output_z, output_w = self.projector.phase_to_coordinate(
            self.state.phi_x, self.state.phi_y, self.state.phi_z, self.state.phi_w
        )
        
        output = Grid4DOutput(
            x=output_x,
            y=output_y,
            z=output_z,
            w=output_w,  # W 좌표 추가 ✨ NEW
            phi_x=self.state.phi_x,
            phi_y=self.state.phi_y,
            phi_z=self.state.phi_z,
            phi_w=self.state.phi_w  # W 위상 추가 ✨ NEW
        )
        
        # 진단 정보 추가 (선택적)
        # 주의: 현재 energy.py는 2D만 지원하므로 4D 진단은 별도 구현 필요
        # TODO: energy_4d.py 구현 또는 energy.py 확장
        if self.config.diagnostics_enabled and self.state_prev is not None:
            # 4D 에너지 계산 (임시: 2D energy 사용 불가, 수동 계산)
            # phase_energy = 0.5 * (phi_x² + phi_y² + phi_z² + phi_w²)
            # kinetic_energy = 0.5 * (vx² + vy² + vz² + vw²)
            # energy = phase_energy + kinetic_energy
            pass  # TODO: 4D 진단 구현
        
        # 에너지 감소 검증 (선택적)
        # TODO: 4D 에너지 검증 구현
        if self.config.energy_check_enabled and self.state_prev is not None:
            pass  # TODO: 4D 에너지 검증
        
        return output
    
    def get_state(self) -> Grid4DState:
        """현재 상태 반환 (4D)"""
        return self.state
    
    def reset(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        """
        상태 리셋 (4D)
        
        Args:
            x: 초기 X 좌표 [m]
            y: 초기 Y 좌표 [m]
            z: 초기 Z 좌표 [m]
            w: 초기 W 좌표 [m] (새로 추가) ✨ NEW
        """
        # 좌표 → 위상 변환 (projector 사용, 4D)
        phi_x, phi_y, phi_z, phi_w = self.projector.coordinate_to_phase(x, y, z, w)
        phi_x = normalize_phase(phi_x, self.config.phase_wrap)
        phi_y = normalize_phase(phi_y, self.config.phase_wrap)
        phi_z = normalize_phase(phi_z, self.config.phase_wrap)
        phi_w = normalize_phase(phi_w, self.config.phase_wrap)  # W 방향 추가 ✨ NEW
        
        self.state = Grid4DState(
            phi_x=phi_x,
            phi_y=phi_y,
            phi_z=phi_z,
            phi_w=phi_w,  # W 위상 추가 ✨ NEW
            x=x,
            y=y,
            z=z,
            w=w,  # W 좌표 추가 ✨ NEW
            v_x=0.0,
            v_y=0.0,
            v_z=0.0,
            v_w=0.0,  # W 속도 추가 ✨ NEW
            a_x=0.0,
            a_y=0.0,
            a_z=0.0,
            a_w=0.0,  # W 가속도 추가 ✨ NEW
            t_ms=0.0
        )
        # TODO: ring_adapter.reset() 구현 (4D)
        # self.ring_adapter.reset()


"""
Ring 7D Adapter
Ring X, Y, Z, A, B 어댑터 (5개 Ring)

이 모듈은 Grid 7D Engine과 Ring Attractor Engine 간의 어댑터입니다.

7D 확장 (7축 시스템):
    - 2D: Ring X, Ring Y (2개)
    - 3D: Ring X, Ring Y, Ring Z (3개)
    - 4D: Ring X, Ring Y, Ring Z, Ring W (4개)
    - 7D: Ring X, Ring Y, Ring Z, Ring A, Ring B, Ring C, Ring D, Ring D, Ring C (7개) ✨ NEW

핵심 구조:
    Grid 7D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ⊗ Ring C ⊗ Ring D
    위상 공간: T⁷ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹ × S¹
    
    7축 시스템 매핑:
        - 위치 Ring (3개): Ring X, Ring Y, Ring Z (위치 위상 안정화)
        - 회전 Ring (4개): Ring A, Ring B, Ring C, Ring D (회전 위상 안정화)

역할:
    - Grid 7D Engine은 Ring 내부 구현을 몰라야 함 (호출만)
    - Ring Adapter가 Ring Attractor Engine을 래핑
    - 각 축마다 독립적인 Ring Attractor 사용

상세 설명:
    - docs/7D_CONCEPT_AND_EQUATIONS.md (7D 개념 및 수식)
    - docs/5AXIS_CNC_APPLICATION.md (7축 시스템 응용)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (7D extension)
License: MIT License
"""

from typing import Tuple, Optional
from dataclasses import dataclass
from .ring_adapter import RingAdapterConfig

# Ring Attractor Engine 의존성 (외부 패키지)
try:
    from ring_attractor_engine.ring_engine import RingAttractorEngine, RingState
except ImportError:
    try:
        from hippo_memory.ring_engine import RingAttractorEngine, RingState
    except ImportError:
        # 로컬 개발 환경: 상대 경로에서 import 시도
        try:
            import sys
            import os
            # ring-attractor-engine 레포지토리 경로 추가
            # 현재 파일 위치: grid-engine/grid_engine/common/adapters/ring_7d_adapter.py
            current_file = os.path.abspath(__file__)
            # grid-engine 디렉토리로 이동 (4단계 상위)
            grid_engine_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            # release 디렉토리로 이동
            release_dir = os.path.dirname(grid_engine_dir)
            # ring-attractor-engine 경로
            ring_engine_path = os.path.join(release_dir, 'ring-attractor-engine')
            
            if os.path.exists(ring_engine_path):
                sys.path.insert(0, ring_engine_path)
                from hippo_memory.ring_engine import RingAttractorEngine, RingState
            else:
                raise ImportError(
                    f"RingAttractorEngine을 찾을 수 없습니다. "
                    f"예상 경로: {ring_engine_path}\n"
                    f"ring-attractor-engine 패키지를 설치하거나, "
                    f"release/ring-attractor-engine 디렉토리에 있어야 합니다."
                )
        except ImportError:
            raise ImportError(
                "RingAttractorEngine을 찾을 수 없습니다. "
                "ring-attractor-engine 패키지를 설치하거나, "
                "release/ring-attractor-engine 디렉토리에 있어야 합니다."
            )


class Ring7DAdapter:
    """
    Ring 7D Adapter
    
    X, Y, Z, A, B 방향 각각의 Ring Engine을 래핑
    Grid7DEngine은 Ring 내부 구현을 몰라야 함
    
    7D 확장 (7축 시스템):
        - 2D: Ring X, Ring Y
        - 3D: Ring X, Ring Y, Ring Z
        - 4D: Ring X, Ring Y, Ring Z, Ring W
        - 7D: Ring X, Ring Y, Ring Z, Ring A, Ring B, Ring C, Ring D, Ring D, Ring C ✨ NEW
    
    7축 시스템 매핑:
        - 위치 Ring (3개): Ring X, Ring Y, Ring Z (위치 위상 안정화)
        - 회전 Ring (4개): Ring A, Ring B, Ring C, Ring D (회전 위상 안정화)
    """
    
    def __init__(
        self,
        config_x: RingAdapterConfig,
        config_y: RingAdapterConfig,
        config_z: RingAdapterConfig,
        config_a: RingAdapterConfig,  # 회전 축 ✨ NEW
        config_b: RingAdapterConfig,  # 회전 축 ✨ NEW
        config_c: RingAdapterConfig,  # 회전 축
        config_d: RingAdapterConfig   # 회전 축
    ):
        """
        Args:
            config_x: X 방향 Ring 설정 (위치)
            config_y: Y 방향 Ring 설정 (위치)
            config_z: Z 방향 Ring 설정 (위치)
            config_a: A 방향 Ring 설정 (회전) ✨ NEW
            config_b: B 방향 Ring 설정 (회전) ✨ NEW
            config_c: C 방향 Ring 설정 (회전)
            config_d: D 방향 Ring 설정 (회전)
        """
        # 위치 Ring (3개)
        self.ring_x = RingAttractorEngine(
            size=config_x.size,
            config=config_x.config,
            seed=config_x.seed,
            debug=config_x.debug
        )
        
        self.ring_y = RingAttractorEngine(
            size=config_y.size,
            config=config_y.config,
            seed=config_y.seed,
            debug=config_y.debug
        )
        
        self.ring_z = RingAttractorEngine(
            size=config_z.size,
            config=config_z.config,
            seed=config_z.seed,
            debug=config_z.debug
        )
        
        # 회전 Ring (4개) ✨ NEW
        self.ring_a = RingAttractorEngine(
            size=config_a.size,
            config=config_a.config,
            seed=config_a.seed,
            debug=config_a.debug
        )
        
        self.ring_b = RingAttractorEngine(
            size=config_b.size,
            config=config_d.config,
            seed=config_d.seed,
            debug=config_d.debug
        )
        
        self.ring_c = RingAttractorEngine(
            size=config_c.size,
            config=config_d.config,
            seed=config_d.seed,
            debug=config_d.debug
        )
        
        self.ring_d = RingAttractorEngine(
            size=config_d.size,
            config=config_d.config,
            seed=config_d.seed,
            debug=config_d.debug
        )
        
        self.config_x = config_x
        self.config_y = config_y
        self.config_z = config_z
        self.config_a = config_a  # 회전 축 ✨ NEW
        self.config_b = config_b  # 회전 축 ✨ NEW
        self.config_c = config_c  # 회전 축
        self.config_d = config_d  # 회전 축
    
    def step(
        self,
        phi_x: float,
        phi_y: float,
        phi_z: float,
        phi_a: float,  # 회전 위상 ✨ NEW
        phi_b: float,  # 회전 위상 ✨ NEW
        phi_c: float,  # 회전 위상
        phi_d: float,  # 회전 위상
        dt_ms: float
    ) -> Tuple[float, float, float, float, float, float, float, Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Ring Engine step 호출 (7D)
        
        각 Ring Attractor에 위상을 주입하고 안정화된 위상을 반환합니다.
        
        Args:
            phi_x: X 방향 위상 (새로운 위상 값) [rad]
            phi_y: Y 방향 위상 (새로운 위상 값) [rad]
            phi_z: Z 방향 위상 (새로운 위상 값) [rad]
            phi_a: A 방향 위상 (새로운 위상 값) [rad] (회전) ✨ NEW
            phi_b: B 방향 위상 (새로운 위상 값) [rad] (회전) ✨ NEW
            phi_c: C 방향 위상 (새로운 위상 값) [rad] (회전)
            phi_d: D 방향 위상 (새로운 위상 값) [rad] (회전)
            dt_ms: 시간 간격 [ms]
        
        Returns:
            (stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_a, stabilized_phi_b, stabilized_phi_c, stabilized_phi_d,
             energy_x, energy_y, energy_z, energy_a, energy_b, energy_c, energy_d)
                - stabilized_phi_*: 안정화된 위상 [rad]
                - energy_*: 에너지 (선택적, 진단용)
        
        알고리즘:
            1. 위상을 Ring 인덱스로 변환
            2. 각 Ring에 위상 주입 및 실행
            3. 안정화된 위상 추출
            4. 원래 위상과 Ring 위상을 가중 평균 (Ring은 미세 조정만)
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 위상을 Ring 인덱스로 변환
        # Ring은 [0, size-1] 범위이므로 위상을 정규화
        size = self.config_x.size
        phase_wrap = 2.0 * 3.141592653589793
        
        # 위상을 [0, 2π) 범위로 정규화
        phi_x_norm = phi_x % phase_wrap
        phi_y_norm = phi_y % phase_wrap
        phi_z_norm = phi_z % phase_wrap
        phi_a_norm = phi_a % phase_wrap  # 회전 위상 ✨ NEW
        phi_b_norm = phi_b % phase_wrap  # 회전 위상 ✨ NEW
        phi_c_norm = phi_c % phase_wrap  # 회전 위상
        phi_d_norm = phi_d % phase_wrap  # 회전 위상
        
        # Ring 인덱스 계산
        idx_x = int((phi_x_norm / phase_wrap) * size) % size
        idx_y = int((phi_y_norm / phase_wrap) * size) % size
        idx_z = int((phi_z_norm / phase_wrap) * size) % size
        idx_a = int((phi_a_norm / phase_wrap) * size) % size  # 회전 인덱스 ✨ NEW
        idx_b = int((phi_b_norm / phase_wrap) * size) % size  # 회전 인덱스 ✨ NEW
        idx_c = int((phi_c_norm / phase_wrap) * size) % size  # 회전 인덱스
        idx_d = int((phi_d_norm / phase_wrap) * size) % size  # 회전 인덱스
        
        # 위치 Ring 주입 및 실행 (X, Y, Z)
        self.ring_x.inject(direction_idx=idx_x, strength=0.8)
        state_x = self.ring_x.run(duration_ms=dt_ms)
        
        self.ring_y.inject(direction_idx=idx_y, strength=0.8)
        state_y = self.ring_y.run(duration_ms=dt_ms)
        
        self.ring_z.inject(direction_idx=idx_z, strength=0.8)
        state_z = self.ring_z.run(duration_ms=dt_ms)
        
        # 회전 Ring 주입 및 실행 (A, B) ✨ NEW
        self.ring_a.inject(direction_idx=idx_a, strength=0.8)
        state_a = self.ring_a.run(duration_ms=dt_ms)
        
        self.ring_b.inject(direction_idx=idx_b, strength=0.8)
        state_b = self.ring_b.run(duration_ms=dt_ms)
        
        self.ring_c.inject(direction_idx=idx_c, strength=0.8)
        state_c = self.ring_c.run(duration_ms=dt_ms)
        
        self.ring_d.inject(direction_idx=idx_d, strength=0.8)
        state_d = self.ring_d.run(duration_ms=dt_ms)
        
        # 안정화된 위상 추출
        # Ring center를 위상으로 변환하되, 원래 위상 값과 혼합
        # (Ring이 위상을 약간 조정하지만, 전체적인 위상은 유지)
        ring_phi_x = (state_x.center / size) * phase_wrap
        ring_phi_y = (state_y.center / size) * phase_wrap
        ring_phi_z = (state_z.center / size) * phase_wrap
        ring_phi_a = (state_a.center / size) * phase_wrap  # 회전 위상 ✨ NEW
        ring_phi_b = (state_b.center / size) * phase_wrap  # 회전 위상 ✨ NEW
        ring_phi_c = (state_c.center / size) * phase_wrap  # 회전 위상
        ring_phi_d = (state_d.center / size) * phase_wrap  # 회전 위상
        
        # 원래 위상과 Ring 위상을 가중 평균 (Ring은 미세 조정만)
        # 가중치: 원래 위상 0.9, Ring 조정 0.1
        stabilized_phi_x = 0.9 * phi_x_norm + 0.1 * ring_phi_x
        stabilized_phi_y = 0.9 * phi_y_norm + 0.1 * ring_phi_y
        stabilized_phi_z = 0.9 * phi_z_norm + 0.1 * ring_phi_z
        stabilized_phi_a = 0.9 * phi_a_norm + 0.1 * ring_phi_a  # 회전 위상 ✨ NEW
        stabilized_phi_b = 0.9 * phi_b_norm + 0.1 * ring_phi_b  # 회전 위상 ✨ NEW
        stabilized_phi_c = 0.9 * phi_c_norm + 0.1 * ring_phi_c  # 회전 위상
        stabilized_phi_d = 0.9 * phi_d_norm + 0.1 * ring_phi_d  # 회전 위상
        
        # 에너지 (선택적, 진단용)
        energy_x = None  # Ring Engine에서 에너지 제공 시 사용
        energy_y = None
        energy_z = None
        energy_a = None  # 회전 Ring 에너지 ✨ NEW
        energy_b = None  # 회전 Ring 에너지 ✨ NEW
        energy_c = None  # 회전 Ring 에너지
        energy_d = None  # 회전 Ring 에너지
        
        return stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_a, stabilized_phi_b, stabilized_phi_c, stabilized_phi_d, \
               energy_x, energy_y, energy_z, energy_a, energy_b, energy_c, energy_d
    
    def reset(self):
        """Ring Engine 리셋 (7D)"""
        # Ring Engine 리셋 (필요시 구현)
        pass


"""
Ring 3D Adapter
Ring X ⊗ Ring Y ⊗ Ring Z 어댑터

3D 확장: 3개 Ring Attractor Engine을 래핑

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
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
            ring_engine_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                'ring-attractor-engine'
            )
            if os.path.exists(ring_engine_path):
                sys.path.insert(0, ring_engine_path)
                from hippo_memory.ring_engine import RingAttractorEngine, RingState
            else:
                raise ImportError(
                    "RingAttractorEngine을 찾을 수 없습니다. "
                    "ring-attractor-engine 패키지를 설치하세요: pip install ring-attractor-engine"
                )
        except ImportError:
            raise ImportError(
                "RingAttractorEngine을 찾을 수 없습니다. "
                "ring-attractor-engine 패키지를 설치하세요: pip install ring-attractor-engine"
            )


class Ring3DAdapter:
    """
    Ring 3D Adapter
    
    X, Y, Z 방향 각각의 Ring Engine을 래핑
    Grid3DEngine은 Ring 내부 구현을 몰라야 함
    
    3D 확장:
        - 2D: Ring X, Ring Y
        - 3D: Ring X, Ring Y, Ring Z
    """
    
    def __init__(
        self,
        config_x: RingAdapterConfig,
        config_y: RingAdapterConfig,
        config_z: RingAdapterConfig
    ):
        """
        Ring 3D Adapter 초기화
        
        Args:
            config_x: X 방향 Ring 설정
            config_y: Y 방향 Ring 설정
            config_z: Z 방향 Ring 설정 (새로 추가)
        """
        # X, Y, Z 방향 Ring Engine 생성
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
        
        self.config_x = config_x
        self.config_y = config_y
        self.config_z = config_z
    
    def step(
        self,
        phi_x: float,
        phi_y: float,
        phi_z: float,
        dt_ms: float
    ) -> Tuple[float, float, float, Optional[float], Optional[float], Optional[float]]:
        """
        Ring Engine step 호출 (3D)
        
        3개 Ring을 독립적으로 실행하여 위상 안정화
        
        Args:
            phi_x: X 방향 위상 (새로운 위상 값) [rad]
            phi_y: Y 방향 위상 (새로운 위상 값) [rad]
            phi_z: Z 방향 위상 (새로운 위상 값) [rad] (새로 추가)
            dt_ms: 시간 간격 [ms]
        
        Returns:
            (stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, energy_x, energy_y, energy_z)
                - stabilized_phi_x, stabilized_phi_y, stabilized_phi_z: 안정화된 위상 [rad]
                - energy_x, energy_y, energy_z: 각 Ring의 에너지 (선택적)
        """
        # 위상을 Ring 인덱스로 변환
        # Ring은 [0, size-1] 범위이므로 위상을 정규화
        size = self.config_x.size
        phase_wrap = 2.0 * 3.141592653589793
        
        # 위상을 [0, 2π) 범위로 정규화
        phi_x_norm = phi_x % phase_wrap
        phi_y_norm = phi_y % phase_wrap
        phi_z_norm = phi_z % phase_wrap  # Z 위상 추가
        
        idx_x = int((phi_x_norm / phase_wrap) * size) % size
        idx_y = int((phi_y_norm / phase_wrap) * size) % size
        idx_z = int((phi_z_norm / phase_wrap) * size) % size  # Z 인덱스 추가
        
        # X 방향 Ring 주입 및 실행
        self.ring_x.inject(direction_idx=idx_x, strength=0.8)
        state_x = self.ring_x.run(duration_ms=dt_ms)
        
        # Y 방향 Ring 주입 및 실행
        self.ring_y.inject(direction_idx=idx_y, strength=0.8)
        state_y = self.ring_y.run(duration_ms=dt_ms)
        
        # Z 방향 Ring 주입 및 실행 (새로 추가)
        self.ring_z.inject(direction_idx=idx_z, strength=0.8)
        state_z = self.ring_z.run(duration_ms=dt_ms)
        
        # 안정화된 위상 추출
        # Ring center를 위상으로 변환하되, 원래 위상 값과 혼합
        # (Ring이 위상을 약간 조정하지만, 전체적인 위상은 유지)
        ring_phi_x = (state_x.center / size) * phase_wrap
        ring_phi_y = (state_y.center / size) * phase_wrap
        ring_phi_z = (state_z.center / size) * phase_wrap  # Z 위상 추가
        
        # 원래 위상과 Ring 위상을 가중 평균 (Ring은 미세 조정만)
        # 가중치: 원래 위상 0.9, Ring 조정 0.1
        stabilized_phi_x = 0.9 * phi_x_norm + 0.1 * ring_phi_x
        stabilized_phi_y = 0.9 * phi_y_norm + 0.1 * ring_phi_y
        stabilized_phi_z = 0.9 * phi_z_norm + 0.1 * ring_phi_z  # Z 위상 추가
        
        # 에너지 (선택적, 진단 모드에서만 사용)
        energy_x = getattr(state_x, 'energy', None)
        energy_y = getattr(state_y, 'energy', None)
        energy_z = getattr(state_z, 'energy', None)
        
        return stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, energy_x, energy_y, energy_z


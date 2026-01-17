"""
Ring 4D Adapter
Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W 어댑터

4D 확장: 4개 Ring Attractor Engine을 래핑

4D 확장:
    - 2D: Ring X, Ring Y
    - 3D: Ring X, Ring Y, Ring Z
    - 4D: Ring X, Ring Y, Ring Z, Ring W ✨ NEW

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
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
            # 현재 파일 위치: grid-engine/grid_engine/common/adapters/ring_4d_adapter.py
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
                "ring-attractor-engine 패키지를 설치하세요: pip install ring-attractor-engine"
            )


class Ring4DAdapter:
    """
    Ring 4D Adapter
    
    X, Y, Z, W 방향 각각의 Ring Engine을 래핑
    Grid4DEngine은 Ring 내부 구현을 몰라야 함
    
    4D 확장:
        - 2D: Ring X, Ring Y
        - 3D: Ring X, Ring Y, Ring Z
        - 4D: Ring X, Ring Y, Ring Z, Ring W ✨ NEW
    """
    
    def __init__(
        self,
        config_x: RingAdapterConfig,
        config_y: RingAdapterConfig,
        config_z: RingAdapterConfig,
        config_w: RingAdapterConfig
    ):
        """
        Ring 4D Adapter 초기화
        
        Args:
            config_x: X 방향 Ring 설정
            config_y: Y 방향 Ring 설정
            config_z: Z 방향 Ring 설정
            config_w: W 방향 Ring 설정 (새로 추가) ✨ NEW
        """
        # X, Y, Z, W 방향 Ring Engine 생성
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
        
        self.ring_w = RingAttractorEngine(
            size=config_w.size,
            config=config_w.config,
            seed=config_w.seed,
            debug=config_w.debug
        )  # W 방향 추가 ✨ NEW
        
        self.config_x = config_x
        self.config_y = config_y
        self.config_z = config_z
        self.config_w = config_w  # W 설정 추가 ✨ NEW
    
    def step(
        self,
        phi_x: float,
        phi_y: float,
        phi_z: float,
        phi_w: float,
        dt_ms: float
    ) -> Tuple[float, float, float, float, Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Ring Engine step 호출 (4D)
        
        4개 Ring을 독립적으로 실행하여 위상 안정화
        
        Args:
            phi_x: X 방향 위상 (새로운 위상 값) [rad]
            phi_y: Y 방향 위상 (새로운 위상 값) [rad]
            phi_z: Z 방향 위상 (새로운 위상 값) [rad]
            phi_w: W 방향 위상 (새로운 위상 값) [rad] (새로 추가) ✨ NEW
            dt_ms: 시간 간격 [ms]
        
        Returns:
            (stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_w, 
             energy_x, energy_y, energy_z, energy_w)
                - stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_w: 안정화된 위상 [rad]
                - energy_x, energy_y, energy_z, energy_w: 각 Ring의 에너지 (선택적)
        """
        # 위상을 Ring 인덱스로 변환
        # Ring은 [0, size-1] 범위이므로 위상을 정규화
        size = self.config_x.size
        phase_wrap = 2.0 * 3.141592653589793
        
        # 위상을 [0, 2π) 범위로 정규화 (4D)
        phi_x_norm = phi_x % phase_wrap
        phi_y_norm = phi_y % phase_wrap
        phi_z_norm = phi_z % phase_wrap
        phi_w_norm = phi_w % phase_wrap  # W 위상 추가 ✨ NEW
        
        idx_x = int((phi_x_norm / phase_wrap) * size) % size
        idx_y = int((phi_y_norm / phase_wrap) * size) % size
        idx_z = int((phi_z_norm / phase_wrap) * size) % size
        idx_w = int((phi_w_norm / phase_wrap) * size) % size  # W 인덱스 추가 ✨ NEW
        
        # X 방향 Ring 주입 및 실행
        self.ring_x.inject(direction_idx=idx_x, strength=0.8)
        state_x = self.ring_x.run(duration_ms=dt_ms)
        
        # Y 방향 Ring 주입 및 실행
        self.ring_y.inject(direction_idx=idx_y, strength=0.8)
        state_y = self.ring_y.run(duration_ms=dt_ms)
        
        # Z 방향 Ring 주입 및 실행
        self.ring_z.inject(direction_idx=idx_z, strength=0.8)
        state_z = self.ring_z.run(duration_ms=dt_ms)
        
        # W 방향 Ring 주입 및 실행 (새로 추가) ✨ NEW
        self.ring_w.inject(direction_idx=idx_w, strength=0.8)
        state_w = self.ring_w.run(duration_ms=dt_ms)
        
        # 안정화된 위상 추출 (4D)
        # Ring center를 위상으로 변환하되, 원래 위상 값과 혼합
        # (Ring이 위상을 약간 조정하지만, 전체적인 위상은 유지)
        ring_phi_x = (state_x.center / size) * phase_wrap
        ring_phi_y = (state_y.center / size) * phase_wrap
        ring_phi_z = (state_z.center / size) * phase_wrap
        ring_phi_w = (state_w.center / size) * phase_wrap  # W 위상 추가 ✨ NEW
        
        # 원래 위상과 Ring 위상을 가중 평균 (Ring은 미세 조정만)
        # 가중치: 원래 위상 0.9, Ring 조정 0.1
        stabilized_phi_x = 0.9 * phi_x_norm + 0.1 * ring_phi_x
        stabilized_phi_y = 0.9 * phi_y_norm + 0.1 * ring_phi_y
        stabilized_phi_z = 0.9 * phi_z_norm + 0.1 * ring_phi_z
        stabilized_phi_w = 0.9 * phi_w_norm + 0.1 * ring_phi_w  # W 위상 추가 ✨ NEW
        
        # 에너지 (선택적, 진단 모드에서만 사용)
        energy_x = getattr(state_x, 'energy', None)
        energy_y = getattr(state_y, 'energy', None)
        energy_z = getattr(state_z, 'energy', None)
        energy_w = getattr(state_w, 'energy', None)  # W 에너지 추가 ✨ NEW
        
        return stabilized_phi_x, stabilized_phi_y, stabilized_phi_z, stabilized_phi_w, \
               energy_x, energy_y, energy_z, energy_w


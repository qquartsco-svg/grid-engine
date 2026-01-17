"""
Ring Adapter
RingAttractorEngine 호출/래핑 (의존성 경계)

GridEngine은 Ring 내부 구현을 몰라야 함 (호출만)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from typing import Optional, Tuple
from dataclasses import dataclass

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


@dataclass
class RingAdapterConfig:
    """Ring Adapter 설정"""
    size: int = 15
    config: str = "case2"
    seed: Optional[int] = None
    debug: bool = False


class RingAdapter:
    """
    Ring Attractor Engine 어댑터
    
    X, Y 방향 각각의 Ring Engine을 래핑
    GridEngine은 Ring 내부 구현을 몰라야 함
    """
    
    def __init__(
        self,
        config_x: RingAdapterConfig,
        config_y: RingAdapterConfig
    ):
        """
        Args:
            config_x: X 방향 Ring 설정
            config_y: Y 방향 Ring 설정
        """
        # X, Y 방향 Ring Engine 생성
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
        
        self.config_x = config_x
        self.config_y = config_y
    
    def step(
        self,
        phi_x: float,
        phi_y: float,
        dt_ms: float
    ) -> Tuple[float, float, Optional[float], Optional[float]]:
        """
        Ring Engine step 호출
        
        Args:
            phi_x: X 방향 위상 (새로운 위상 값)
            phi_y: Y 방향 위상 (새로운 위상 값)
            dt_ms: 시간 간격 [ms]
        
        Returns:
            (stabilized_phi_x, stabilized_phi_y, energy_x, energy_y)
        """
        # 위상을 Ring 인덱스로 변환
        # Ring은 [0, size-1] 범위이므로 위상을 정규화
        size = self.config_x.size
        phase_wrap = 2.0 * 3.141592653589793
        
        # 위상을 [0, 2π) 범위로 정규화
        phi_x_norm = phi_x % phase_wrap
        phi_y_norm = phi_y % phase_wrap
        
        idx_x = int((phi_x_norm / phase_wrap) * size) % size
        idx_y = int((phi_y_norm / phase_wrap) * size) % size
        
        # X 방향 Ring 주입 및 실행
        # 주의: inject는 위상을 "설정"하는 것이 아니라 "주입"하는 것
        # 위상이 이미 업데이트되었으므로, 이를 Ring에 반영
        self.ring_x.inject(direction_idx=idx_x, strength=0.8)
        state_x = self.ring_x.run(duration_ms=dt_ms)
        
        # Y 방향 Ring 주입 및 실행
        self.ring_y.inject(direction_idx=idx_y, strength=0.8)
        state_y = self.ring_y.run(duration_ms=dt_ms)
        
        # 안정화된 위상 추출
        # Ring center를 위상으로 변환하되, 원래 위상 값과 혼합
        # (Ring이 위상을 약간 조정하지만, 전체적인 위상은 유지)
        ring_phi_x = (state_x.center / size) * phase_wrap
        ring_phi_y = (state_y.center / size) * phase_wrap
        
        # 원래 위상과 Ring 위상을 가중 평균 (Ring은 미세 조정만)
        # 가중치: 원래 위상 0.9, Ring 조정 0.1
        stabilized_phi_x = 0.9 * phi_x_norm + 0.1 * ring_phi_x
        stabilized_phi_y = 0.9 * phi_y_norm + 0.1 * ring_phi_y
        
        # 에너지 (선택적, 진단용)
        energy_x = None  # Ring Engine에서 에너지 제공 시 사용
        energy_y = None
        
        return stabilized_phi_x, stabilized_phi_y, energy_x, energy_y
    
    def reset(self):
        """Ring Engine 리셋"""
        # Ring Engine 리셋 (필요시 구현)
        pass


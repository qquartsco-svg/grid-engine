"""
Grid Engine 7D Config
7D 설정 (독립 모듈)

이 모듈은 Grid 7D Engine의 설정을 정의합니다.

7D 확장 (7축 시스템):
    - 2D: GridEngineConfig (X, Y)
    - 3D: Grid3DConfig (X, Y, Z)
    - 4D: Grid4DConfig (X, Y, Z, W)
    - 7D: Grid7DConfig (X, Y, Z, A, B, C, D) ✨ NEW

핵심 구조:
    Grid 7D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ⊗ Ring C ⊗ Ring D
    위상 공간: T⁷ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹ × S¹
    
    7축 시스템 매핑:
        - 위치 축 (3개): X, Y, Z (선형 이동) [m]
        - 회전 축 (2개): A, B (각도 회전) [deg]

설정 항목:
    - 위치 축: spatial_scale_x, spatial_scale_y, spatial_scale_z [m]
    - 회전 축: angular_scale_a, angular_scale_b [deg] 또는 [rad]
    - Ring 설정: 각 축마다 독립적인 Ring Attractor 설정
    - 시간 설정: dt_ms, tau_ms, max_dt_ratio

상세 설명:
    - docs/7D_CONCEPT_AND_EQUATIONS.md (7D 개념 및 수식)
    - docs/5AXIS_CNC_APPLICATION.md (7축 시스템 응용)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (7D extension)
License: MIT License
"""

from dataclasses import dataclass, field
from typing import Optional
import math

# Ring Attractor Engine 설정 타입 (외부 패키지)
try:
    from ring_attractor_engine.ring_engine_config import RingEngineConfig
except ImportError:
    try:
        from hippo_memory.ring_engine_config import RingEngineConfig
    except ImportError:
        # 로컬 개발 환경
        try:
            import sys
            import os
            current_file = os.path.abspath(__file__)
            grid_engine_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            release_dir = os.path.dirname(grid_engine_dir)
            ring_engine_path = os.path.join(release_dir, 'ring-attractor-engine')
            if os.path.exists(ring_engine_path):
                sys.path.insert(0, ring_engine_path)
                from hippo_memory.ring_engine_config import RingEngineConfig
            else:
                # Fallback: 간단한 타입 정의
                from typing import Any
                RingEngineConfig = Any
        except ImportError:
            from typing import Any
            RingEngineConfig = Any


@dataclass
class Grid7DConfig:
    """
    Grid 7D Engine 설정
    
    7D 확장 (7축 시스템):
        - 2D: GridEngineConfig (X, Y)
        - 3D: Grid3DConfig (X, Y, Z)
        - 4D: Grid4DConfig (X, Y, Z, W)
        - 7D: Grid7DConfig (X, Y, Z, A, B, C, D) ✨ NEW
    
    설정 항목:
        - 위치 축: spatial_scale_x, spatial_scale_y, spatial_scale_z [m]
        - 회전 축: angular_scale_a, angular_scale_b [deg] 또는 [rad]
        - Ring 설정: 각 축마다 독립적인 Ring Attractor 설정
        - 시간 설정: dt_ms, tau_ms, max_dt_ratio
    
    7축 시스템 매핑:
        - X, Y, Z: 위치 축 (선형 이동) [m]
        - A, B: 회전 축 (각도 회전) [deg]
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # 위치 축 공간 스케일 [m]
    spatial_scale_x: float = 1.0  # X축 공간 스케일 Lx [m]
    spatial_scale_y: float = 1.0  # Y축 공간 스케일 Ly [m]
    spatial_scale_z: float = 1.0  # Z축 공간 스케일 Lz [m]
    
    # 회전 축 각도 스케일 [deg]
    # 주의: 회전 축은 각도 단위를 사용 (360° = 2π rad)
    angular_scale_a: float = 360.0  # A축 각도 스케일 [deg] (전체 회전 범위)
    angular_scale_b: float = 360.0  # B축 각도 스케일 [deg] (전체 회전 범위)
    angular_scale_c: float = 360.0  # C축 각도 스케일 [deg]
    angular_scale_d: float = 360.0  # D축 각도 스케일 [deg]
    
    # 위상 래핑 (공통)
    phase_wrap: float = 2.0 * math.pi  # 위상 래핑 값 [rad] (2π)
    
    # 시간 설정
    dt_ms: float = 0.1  # 시간 간격 [ms]
    tau_ms: float = 10.0  # 시간 상수 [ms]
    max_dt_ratio: float = 0.1  # 최대 dt 비율 (dt_ms < tau_ms * max_dt_ratio)
    
    # Ring 설정 (각 축마다 독립적)
    ring_size: int = 15  # Ring 크기 (공통)
    ring_cfg_x: Optional[RingEngineConfig] = None  # X축 Ring 설정
    ring_cfg_y: Optional[RingEngineConfig] = None  # Y축 Ring 설정
    ring_cfg_z: Optional[RingEngineConfig] = None  # Z축 Ring 설정
    ring_cfg_a: Optional[RingEngineConfig] = None  # A축 Ring 설정 ✨ NEW
    ring_cfg_b: Optional[RingEngineConfig] = None  # B축 Ring 설정 ✨ NEW
    ring_cfg_c: Optional[RingEngineConfig] = None  # C축 Ring 설정
    ring_cfg_d: Optional[RingEngineConfig] = None  # D축 Ring 설정
    
    # 진단 설정
    diagnostics_enabled: bool = False  # 진단 모드 활성화
    energy_check_enabled: bool = False  # 에너지 검증 활성화
    
    # 수치 적분 방법
    integration_method: str = "semi_implicit_euler"  # 수치 적분 방법
    
    def __post_init__(self):
        """
        설정 검증
        
        모든 설정 값이 유효한 범위에 있는지 확인합니다.
        """
        # 공간 스케일 검증 (위치 축)
        assert self.spatial_scale_x > 0, f"spatial_scale_x ({self.spatial_scale_x}) must be > 0"
        assert self.spatial_scale_y > 0, f"spatial_scale_y ({self.spatial_scale_y}) must be > 0"
        assert self.spatial_scale_z > 0, f"spatial_scale_z ({self.spatial_scale_z}) must be > 0"
        
        # 각도 스케일 검증 (회전 축)
        assert self.angular_scale_a > 0, f"angular_scale_a ({self.angular_scale_a}) must be > 0"
        assert self.angular_scale_b > 0, f"angular_scale_b ({self.angular_scale_b}) must be > 0"
        assert self.angular_scale_c > 0, f"angular_scale_c ({self.angular_scale_c}) must be > 0"
        assert self.angular_scale_d > 0, f"angular_scale_d ({self.angular_scale_d}) must be > 0"
        
        # 위상 래핑 검증
        assert self.phase_wrap > 0, f"phase_wrap ({self.phase_wrap}) must be > 0"
        
        # 시간 설정 검증
        assert self.dt_ms > 0, f"dt_ms ({self.dt_ms}) must be > 0"
        assert self.tau_ms > 0, f"tau_ms ({self.tau_ms}) must be > 0"
        assert self.max_dt_ratio > 0, f"max_dt_ratio ({self.max_dt_ratio}) must be > 0"
        assert self.dt_ms < self.tau_ms * self.max_dt_ratio, \
            f"dt_ms ({self.dt_ms}) must be < tau_ms * max_dt_ratio ({self.tau_ms * self.max_dt_ratio})"
        
        # Ring 크기 검증
        assert self.ring_size > 0, f"ring_size ({self.ring_size}) must be > 0"
        
        # 수치 적분 방법 검증
        assert self.integration_method in ["semi_implicit_euler"], \
            f"integration_method ({self.integration_method}) must be 'semi_implicit_euler'"
    
    def validate(self):
        """
        설정 검증 (명시적 호출)
        
        __post_init__에서 자동으로 호출되지만, 명시적으로도 호출 가능합니다.
        """
        self.__post_init__()


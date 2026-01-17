"""
Grid Engine 3D Configuration
3D 상수/튜닝 파라미터 (하드코딩 금지)

3D 확장: Ring X ⊗ Ring Y ⊗ Ring Z
Z 방향 설정 추가

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
License: MIT License
"""

from dataclasses import dataclass
from ..dim2d.config_2d import GridEngineConfig


@dataclass
class Grid3DConfig(GridEngineConfig):
    """
    Grid 3D Engine 설정
    
    2D 설정을 확장하여 Z 방향 설정 추가
    
    3D 확장:
        - 2D: ring_cfg_x, ring_cfg_y
        - 3D: ring_cfg_x, ring_cfg_y, ring_cfg_z
        
        - 2D: spatial_scale_x, spatial_scale_y
        - 3D: spatial_scale_x, spatial_scale_y, spatial_scale_z
    """
    # Ring Engine 설정 (Z 방향 추가)
    ring_cfg_z: str = "case2"  # Z 방향 Ring 설정
    
    # 공간 스케일 (Z 방향 추가)
    # spatial_scale_z: 위상 2π가 대응하는 실제 공간 길이 [m]
    # z = phi_z * (spatial_scale_z / 2π)
    spatial_scale_z: float = 1.0  # Z 방향 도메인 길이 [m] (2π rad에 대응)
    
    def validate(self) -> None:
        """
        설정 유효성 검증 (3D)
        
        2D 검증 + Z 방향 검증 추가
        
        검증 항목:
            - 2D 검증 항목 (상위 클래스 호출)
            - ring_cfg_z: 유효한 설정 이름
            - spatial_scale_z > 0: Z 공간 스케일은 양수여야 함
        
        Raises:
            AssertionError: 설정이 유효하지 않은 경우
        """
        # 2D 검증 (상위 클래스 호출)
        super().validate()
        
        # Z 방향 검증
        assert self.spatial_scale_z > 0, "spatial_scale_z must be positive"
        
        # Ring 설정 검증 (간단한 검증)
        assert isinstance(self.ring_cfg_z, str), "ring_cfg_z must be a string"
        assert len(self.ring_cfg_z) > 0, "ring_cfg_z must not be empty"


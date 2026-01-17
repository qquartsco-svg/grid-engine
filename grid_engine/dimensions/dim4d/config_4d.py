"""
Grid Engine 4D Configuration
4D 상수/튜닝 파라미터 (하드코딩 금지)

4D 확장: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W
W 방향 설정 추가

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

from dataclasses import dataclass
from ..dim3d.config_3d import Grid3DConfig


@dataclass
class Grid4DConfig(Grid3DConfig):
    """
    Grid 4D Engine 설정
    
    3D 설정을 확장하여 W 방향 설정 추가
    
    4D 확장:
        - 2D: ring_cfg_x, ring_cfg_y
        - 3D: ring_cfg_x, ring_cfg_y, ring_cfg_z
        - 4D: ring_cfg_x, ring_cfg_y, ring_cfg_z, ring_cfg_w ✨ NEW
        
        - 2D: spatial_scale_x, spatial_scale_y
        - 3D: spatial_scale_x, spatial_scale_y, spatial_scale_z
        - 4D: spatial_scale_x, spatial_scale_y, spatial_scale_z, spatial_scale_w ✨ NEW
    
    위상 공간:
        T⁴ = S¹ × S¹ × S¹ × S¹ (4차원 토러스)
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # Ring Engine 설정 (W 방향 추가)
    ring_cfg_w: str = "case2"  # W 방향 Ring 설정 ✨ NEW
    
    # 공간 스케일 (W 방향 추가)
    # spatial_scale_w: 위상 2π가 대응하는 실제 공간 길이 [m]
    # w = phi_w * (spatial_scale_w / 2π)
    spatial_scale_w: float = 1.0  # W 방향 도메인 길이 [m] (2π rad에 대응) ✨ NEW
    
    def validate(self) -> None:
        """
        설정 유효성 검증 (4D)
        
        3D 검증 + W 방향 검증 추가
        
        검증 항목:
            - 3D 검증 항목 (상위 클래스 호출)
            - ring_cfg_w: 유효한 설정 이름
            - spatial_scale_w > 0: W 공간 스케일은 양수여야 함
        
        Raises:
            AssertionError: 설정이 유효하지 않은 경우
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 3D 검증 (상위 클래스 호출)
        super().validate()
        
        # W 방향 검증 ✨ NEW
        assert self.spatial_scale_w > 0, "spatial_scale_w must be positive"
        
        # Ring 설정 검증 (간단한 검증)
        assert isinstance(self.ring_cfg_w, str), "ring_cfg_w must be a string"
        assert len(self.ring_cfg_w) > 0, "ring_cfg_w must not be empty"


"""
Coordinate Projector (4D)
위상 → 4D 좌표 투영 (관측자 책임)

이 모듈은 Grid 4D Engine의 내부 위상을 외부 4D 좌표로 투영합니다.
Grid 4D Engine은 내부 위상(phi_x, phi_y, phi_z, phi_w)만 관리하고, 좌표 투영은 이 모듈(관측자)의 책임입니다.

4D 확장:
    - 2D: 위상 (φx, φy) → 좌표 (x, y)
    - 3D: 위상 (φx, φy, φz) → 좌표 (x, y, z)
    - 4D: 위상 (φx, φy, φz, φw) → 좌표 (x, y, z, w) ✨ NEW

아키텍처 원칙:
    책임 분리(Separation of Concerns):
        - Grid 4D Engine: 내부 위상 상태만 관리 (φx, φy, φz, φw)
        - Coordinate4DProjector: 위상 → 4D 좌표 변환 (관측자 패턴)

핵심 개념:
    내부 상태: 위상 φ ∈ [0, 2π) × [0, 2π) × [0, 2π) × [0, 2π) [rad⁴] (주기적 공간)
    외부 표현: 좌표 (x, y, z, w) [m⁴] (선형 공간)
    변환 관계: 
        x = φx · (Lx / 2π)
        y = φy · (Ly / 2π)
        z = φz · (Lz / 2π)
        w = φw · (Lw / 2π)  ← W 방향 추가 ✨ NEW

수학적 배경:
    Grid 4D Engine은 토러스(Torus) T⁴ = S¹ × S¹ × S¹ × S¹에서 동작합니다.
    위상은 주기적 경계 조건을 만족하지만,
    좌표는 사용자가 원하는 스케일로 투영할 수 있습니다.

상세 설명:
    - docs/4D_CONCEPT_AND_EQUATIONS.md (4D 개념 및 수식)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

from typing import Tuple
from .types_4d import Grid4DState
from .config_4d import Grid4DConfig


class Coordinate4DProjector:
    """
    4D 좌표 투영기 (Observer)
    
    Grid 4D Engine의 내부 위상을 외부 4D 좌표로 투영합니다.
    Grid 4D Engine은 위상만 유지하고, 좌표 계산은 이 클래스가 담당합니다.
    
    4D 확장:
        - 2D: (φx, φy) → (x, y)
        - 3D: (φx, φy, φz) → (x, y, z)
        - 4D: (φx, φy, φz, φw) → (x, y, z, w) ✨ NEW
    """
    
    def __init__(self, config: Grid4DConfig):
        """
        Args:
            config: Grid 4D Engine 설정
        """
        self.config = config
    
    def phase_to_coordinate(
        self,
        phi_x: float,
        phi_y: float,
        phi_z: float,
        phi_w: float
    ) -> Tuple[float, float, float, float]:
        """
        위상 → 4D 좌표 변환
        
        내부 위상(Phase)을 외부 4D 좌표(Coordinate)로 변환합니다.
        Grid 4D Engine의 내부 상태를 외부 세계의 4D 위치로 투영합니다.
        
        수학적 배경:
            Grid 4D Engine은 토러스 T⁴ = S¹ × S¹ × S¹ × S¹에서 동작합니다.
            위상 φ ∈ [0, 2π)는 주기적 공간의 위치를 나타냅니다.
            좌표 (x, y, z, w) ∈ [0, L)⁴는 실제 4D 공간의 위치를 나타냅니다.
        
        변환 수식:
            x = φx · (Lx / 2π)
            y = φy · (Ly / 2π)
            z = φz · (Lz / 2π)
            w = φw · (Lw / 2π)  ← W 방향 추가 ✨ NEW
            
            여기서:
                - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
                - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
                - Lz = spatial_scale_z: Z 방향 도메인 길이 [m]
                - Lw = spatial_scale_w: W 방향 도메인 길이 [m] ✨ NEW
                - 2π = phase_wrap: 위상 범위 [rad]
        
        단위 분석:
            x [m] = φx [rad] * (Lx [m] / 2π [rad])
            y [m] = φy [rad] * (Ly [m] / 2π [rad])
            z [m] = φz [rad] * (Lz [m] / 2π [rad])
            w [m] = φw [rad] * (Lw [m] / 2π [rad])  ← W 방향 추가 ✨ NEW
        
        물리적 의미:
            위상 2π [rad]가 실제 공간 L [m]에 대응됩니다.
            예: L = 10.0 m → 2π rad = 10.0 m → 1 rad ≈ 1.59 m
        
        Args:
            phi_x: X 방향 위상 [0, 2π) [rad]
            phi_y: Y 방향 위상 [0, 2π) [rad]
            phi_z: Z 방향 위상 [0, 2π) [rad]
            phi_w: W 방향 위상 [0, 2π) [rad] (새로 추가) ✨ NEW
        
        Returns:
            (x, y, z, w) 좌표 [m]
                - x: X 방향 좌표 [m]
                - y: Y 방향 좌표 [m]
                - z: Z 방향 좌표 [m]
                - w: W 방향 좌표 [m] (새로 추가) ✨ NEW
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 변환 수식: x = φx · (Lx / 2π)
        x = phi_x * (self.config.spatial_scale_x / self.config.phase_wrap)
        y = phi_y * (self.config.spatial_scale_y / self.config.phase_wrap)
        z = phi_z * (self.config.spatial_scale_z / self.config.phase_wrap)
        w = phi_w * (self.config.spatial_scale_w / self.config.phase_wrap)  # W 방향 추가 ✨ NEW
        return x, y, z, w
    
    def coordinate_to_phase(
        self,
        x: float,
        y: float,
        z: float,
        w: float
    ) -> Tuple[float, float, float, float]:
        """
        좌표 → 위상 변환 (4D)
        
        외부 4D 좌표(Coordinate)를 내부 위상(Phase)으로 변환합니다.
        외부 세계의 4D 위치를 Grid 4D Engine의 내부 상태로 투영합니다.
        
        수학적 배경:
            phase_to_coordinate_4d()의 역변환입니다.
            좌표 (x, y, z, w) ∈ [0, L)⁴ → 위상 (φx, φy, φz, φw) ∈ [0, 2π)⁴
        
        변환 수식:
            φx = x · (2π / Lx)
            φy = y · (2π / Ly)
            φz = z · (2π / Lz)
            φw = w · (2π / Lw)  ← W 방향 추가 ✨ NEW
            
            여기서:
                - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
                - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
                - Lz = spatial_scale_z: Z 방향 도메인 길이 [m]
                - Lw = spatial_scale_w: W 방향 도메인 길이 [m] ✨ NEW
                - 2π = phase_wrap: 위상 범위 [rad]
        
        단위 분석:
            φx [rad] = x [m] * (2π [rad] / Lx [m])
            φy [rad] = y [m] * (2π [rad] / Ly [m])
            φz [rad] = z [m] * (2π [rad] / Lz [m])
            φw [rad] = w [m] * (2π [rad] / Lw [m])  ← W 방향 추가 ✨ NEW
        
        물리적 의미:
            실제 공간 L [m]가 위상 2π [rad]에 대응됩니다.
            예: L = 10.0 m → 10.0 m = 2π rad → 1 m ≈ 0.628 rad
        
        Args:
            x: X 방향 좌표 [m]
            y: Y 방향 좌표 [m]
            z: Z 방향 좌표 [m]
            w: W 방향 좌표 [m] (새로 추가) ✨ NEW
        
        Returns:
            (phi_x, phi_y, phi_z, phi_w) 위상 [rad]
                - phi_x: X 방향 위상 [rad] (정규화되지 않음)
                - phi_y: Y 방향 위상 [rad] (정규화되지 않음)
                - phi_z: Z 방향 위상 [rad] (정규화되지 않음)
                - phi_w: W 방향 위상 [rad] (정규화되지 않음) (새로 추가) ✨ NEW
        
        주의:
            반환된 위상은 [0, 2π) 범위를 벗어날 수 있습니다.
            normalize_phase()를 사용하여 정규화해야 합니다.
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 변환 수식: φx = x · (2π / Lx)
        phi_x = x * (self.config.phase_wrap / self.config.spatial_scale_x)
        phi_y = y * (self.config.phase_wrap / self.config.spatial_scale_y)
        phi_z = z * (self.config.phase_wrap / self.config.spatial_scale_z)
        phi_w = w * (self.config.phase_wrap / self.config.spatial_scale_w)  # W 방향 추가 ✨ NEW
        return phi_x, phi_y, phi_z, phi_w
    
    def project_state(self, state: Grid4DState) -> Tuple[float, float, float, float]:
        """
        상태의 위상을 4D 좌표로 투영
        
        Args:
            state: Grid 4D 상태 (위상 포함)
        
        Returns:
            (x, y, z, w) 좌표 [m]
        """
        return self.phase_to_coordinate(state.phi_x, state.phi_y, state.phi_z, state.phi_w)


def create_projector_4d(config: Grid4DConfig) -> Coordinate4DProjector:
    """
    Coordinate4DProjector 생성
    
    Args:
        config: Grid 4D Engine 설정
    
    Returns:
        Coordinate4DProjector 인스턴스
    """
    return Coordinate4DProjector(config)


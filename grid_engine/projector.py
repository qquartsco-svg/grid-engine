"""
Coordinate Projector
위상 → 좌표 투영 (관측자 책임)

이 모듈은 Grid Engine의 내부 위상을 외부 좌표로 투영합니다.
Grid Engine은 내부 위상(phi)만 관리하고, 좌표 투영은 이 모듈(관측자)의 책임입니다.

아키텍처 원칙:
    책임 분리(Separation of Concerns):
        - Grid Engine: 내부 위상 상태만 관리
        - CoordinateProjector: 위상 → 좌표 변환 (관측자 패턴)

핵심 개념:
    내부 상태: 위상 φ ∈ [0, 2π) [rad] (주기적 공간)
    외부 표현: 좌표 (x, y) [m] (선형 공간)
    변환 관계: x = φx · (Lx / 2π), φx = x · (2π / Lx)

수학적 배경:
    Grid Engine은 토러스(Torus) T² = S¹ × S¹에서 동작합니다.
    위상은 주기적 경계 조건을 만족하지만,
    좌표는 사용자가 원하는 스케일로 투영할 수 있습니다.

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from typing import Tuple
from .types import GridState
from .config import GridEngineConfig


class CoordinateProjector:
    """
    좌표 투영기 (Observer)
    
    Grid Engine의 내부 위상을 외부 좌표로 투영합니다.
    Grid Engine은 위상만 유지하고, 좌표 계산은 이 클래스가 담당합니다.
    """
    
    def __init__(self, config: GridEngineConfig):
        """
        Args:
            config: Grid Engine 설정
        """
        self.config = config
    
    def phase_to_coordinate(
        self,
        phi_x: float,
        phi_y: float
    ) -> Tuple[float, float]:
        """
        위상 → 좌표 변환
        
        내부 위상(Phase)을 외부 좌표(Coordinate)로 변환합니다.
        Grid Engine의 내부 상태를 외부 세계의 위치로 투영합니다.
        
        수학적 배경:
            Grid Engine은 토러스 T² = S¹ × S¹에서 동작합니다.
            위상 φ ∈ [0, 2π)는 주기적 공간의 위치를 나타냅니다.
            좌표 x ∈ [0, L)는 실제 공간의 위치를 나타냅니다.
        
        변환 수식:
            x = φx · (Lx / 2π)
            y = φy · (Ly / 2π)
            
            여기서:
                - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
                - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
                - 2π = phase_wrap: 위상 범위 [rad]
        
        단위 분석:
            x [m] = φx [rad] * (Lx [m] / 2π [rad])
            y [m] = φy [rad] * (Ly [m] / 2π [rad])
        
        물리적 의미:
            위상 2π [rad]가 실제 공간 L [m]에 대응됩니다.
            예: L = 10.0 m → 2π rad = 10.0 m → 1 rad ≈ 1.59 m
        
        Args:
            phi_x: X 방향 위상 [0, 2π) [rad]
            phi_y: Y 방향 위상 [0, 2π) [rad]
        
        Returns:
            (x, y) 좌표 [m]
                - x: X 방향 좌표 [m]
                - y: Y 방향 좌표 [m]
        
        Author: [작성자 시그니처]
        Created: 2026-01
        """
        # 변환 수식: x = φx · (Lx / 2π)
        x = phi_x * (self.config.spatial_scale_x / self.config.phase_wrap)
        y = phi_y * (self.config.spatial_scale_y / self.config.phase_wrap)
        return x, y
    
    def coordinate_to_phase(
        self,
        x: float,
        y: float
    ) -> Tuple[float, float]:
        """
        좌표 → 위상 변환
        
        외부 좌표(Coordinate)를 내부 위상(Phase)으로 변환합니다.
        외부 세계의 위치를 Grid Engine의 내부 상태로 투영합니다.
        
        수학적 배경:
            phase_to_coordinate()의 역변환입니다.
            좌표 x ∈ [0, L) → 위상 φ ∈ [0, 2π)
        
        변환 수식:
            φx = x · (2π / Lx)
            φy = y · (2π / Ly)
            
            여기서:
                - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
                - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
                - 2π = phase_wrap: 위상 범위 [rad]
        
        단위 분석:
            φx [rad] = x [m] * (2π [rad] / Lx [m])
            φy [rad] = y [m] * (2π [rad] / Ly [m])
        
        물리적 의미:
            실제 공간 L [m]가 위상 2π [rad]에 대응됩니다.
            예: L = 10.0 m → 10.0 m = 2π rad → 1 m ≈ 0.628 rad
        
        Args:
            x: X 방향 좌표 [m]
            y: Y 방향 좌표 [m]
        
        Returns:
            (phi_x, phi_y) 위상 [rad]
                - phi_x: X 방향 위상 [rad] (정규화되지 않음)
                - phi_y: Y 방향 위상 [rad] (정규화되지 않음)
        
        주의:
            반환된 위상은 [0, 2π) 범위를 벗어날 수 있습니다.
            normalize_phase()를 사용하여 정규화해야 합니다.
        
        Author: [작성자 시그니처]
        Created: 2026-01
        """
        # 변환 수식: φx = x · (2π / Lx)
        phi_x = x * (self.config.phase_wrap / self.config.spatial_scale_x)
        phi_y = y * (self.config.phase_wrap / self.config.spatial_scale_y)
        return phi_x, phi_y
    
    def project_state(self, state: GridState) -> Tuple[float, float]:
        """
        상태의 위상을 좌표로 투영
        
        Args:
            state: Grid 상태 (위상 포함)
        
        Returns:
            (x, y) 좌표 [m]
        """
        return self.phase_to_coordinate(state.phi_x, state.phi_y)


def create_projector(config: GridEngineConfig) -> CoordinateProjector:
    """
    CoordinateProjector 생성
    
    Args:
        config: Grid Engine 설정
    
    Returns:
        CoordinateProjector 인스턴스
    """
    return CoordinateProjector(config)


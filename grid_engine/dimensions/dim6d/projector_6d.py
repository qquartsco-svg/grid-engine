"""
Coordinate Projector (6D)
위상 → 6D 좌표/각도 투영 (관측자 책임)

이 모듈은 Grid 6D Engine의 내부 위상을 외부 6D 좌표/각도로 투영합니다.
Grid 6D Engine은 내부 위상(phi_x, phi_y, phi_z, phi_a, phi_b)만 관리하고, 좌표/각도 투영은 이 모듈(관측자)의 책임입니다.

6D 확장 (6축 시스템):
    - 2D: 위상 (φx, φy) → 좌표 (x, y)
    - 3D: 위상 (φx, φy, φz) → 좌표 (x, y, z)
    - 4D: 위상 (φx, φy, φz, φw) → 좌표 (x, y, z, w)
    - 6D: 위상 (φx, φy, φz, φa, φb, φc) → 좌표/각도 (x, y, z, θa, θb, θc) ✨ NEW

아키텍처 원칙:
    책임 분리(Separation of Concerns):
        - Grid 6D Engine: 내부 위상 상태만 관리 (φx, φy, φz, φa, φb, φc)
        - Coordinate6DProjector: 위상 → 6D 좌표/각도 변환 (관측자 패턴)

핵심 개념:
    내부 상태: 위상 φ ∈ [0, 2π)⁵ [rad⁵] (주기적 공간)
    외부 표현:
        - 위치: (x, y, z) [m³] (선형 공간)
        - 각도: (θa, θb) [deg²] (회전 공간)
    변환 관계:
        위치:
            x = φx · (Lx / 2π)
            y = φy · (Ly / 2π)
            z = φz · (Lz / 2π)
        각도:
            θa = φa · (180° / π) = φa · (360° / 2π)
            θb = φb · (180° / π) = φb · (360° / 2π)

수학적 배경:
    Grid 6D Engine은 토러스(Torus) T⁶ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹에서 동작합니다.
    위상은 주기적 경계 조건을 만족하지만,
    좌표/각도는 사용자가 원하는 스케일로 투영할 수 있습니다.

상세 설명:
    - docs/6D_CONCEPT_AND_EQUATIONS.md (6D 개념 및 수식)
    - docs/5AXIS_CNC_APPLICATION.md (6축 시스템 응용)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (6D extension)
License: MIT License
"""

from typing import Tuple
import math
from .types_6d import Grid6DState
from .config_6d import Grid6DConfig


class Coordinate6DProjector:
    """
    6D 좌표/각도 투영기 (Observer)
    
    Grid 6D Engine의 내부 위상을 외부 6D 좌표/각도로 투영합니다.
    Grid 6D Engine은 위상만 유지하고, 좌표/각도 계산은 이 클래스가 담당합니다.
    
    6D 확장 (6축 시스템):
        - 2D: (φx, φy) → (x, y)
        - 3D: (φx, φy, φz) → (x, y, z)
        - 4D: (φx, φy, φz, φw) → (x, y, z, w)
        - 6D: (φx, φy, φz, φa, φb, φc) → (x, y, z, θa, θb, θc) ✨ NEW
    
    6축 시스템 매핑:
        - 위치: (x, y, z) [m]
        - 회전: (θa, θb) [deg]
    """
    
    def __init__(self, config: Grid6DConfig):
        """
        Args:
            config: Grid 6D Engine 설정
        """
        self.config = config
    
    def phase_to_coordinate(
        self,
        phi_x: float,
        phi_y: float,
        phi_z: float,
        phi_a: float,
        phi_b: float,
        phi_c: float  # C 방향 위상 [0, 2π) [rad] (회전)
    ) -> Tuple[float, float, float, float, float, float]:
        """
        위상 → 6D 좌표/각도 변환
        
        내부 위상(Phase)을 외부 6D 좌표/각도(Coordinate/Angle)로 변환합니다.
        Grid 6D Engine의 내부 상태를 외부 세계의 6D 위치/각도로 투영합니다.
        
        수학적 배경:
            Grid 6D Engine은 토러스 T⁶ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹에서 동작합니다.
            위상 φ ∈ [0, 2π)는 주기적 공간의 위치를 나타냅니다.
            좌표 (x, y, z) ∈ [0, L)³는 실제 3D 공간의 위치를 나타냅니다.
            각도 (θa, θb) ∈ [0, 360°)²는 회전 공간의 각도를 나타냅니다.
        
        변환 수식 (위치):
            x = φx · (Lx / 2π)
            y = φy · (Ly / 2π)
            z = φz · (Lz / 2π)
            
            여기서:
                - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
                - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
                - Lz = spatial_scale_z: Z 방향 도메인 길이 [m]
                - 2π = phase_wrap: 위상 범위 [rad]
        
        변환 수식 (각도):
            θa = φa · (360° / 2π) = φa · (180° / π)
            θb = φb · (360° / 2π) = φb · (180° / π)
            
            여기서:
                - 360° = angular_scale_a: A축 각도 스케일 [deg] (전체 회전 범위)
                - 360° = angular_scale_b: B축 각도 스케일 [deg] (전체 회전 범위)
                - 2π = phase_wrap: 위상 범위 [rad]
        
        단위 분석:
            위치:
                x [m] = φx [rad] * (Lx [m] / 2π [rad])
                y [m] = φy [rad] * (Ly [m] / 2π [rad])
                z [m] = φz [rad] * (Lz [m] / 2π [rad])
            각도:
                θa [deg] = φa [rad] * (360° / 2π [rad]) = φa [rad] * (180° / π [rad])
                θb [deg] = φb [rad] * (360° / 2π [rad]) = φb [rad] * (180° / π [rad])
        
        물리적 의미:
            위치:
                위상 2π [rad]가 실제 공간 L [m]에 대응됩니다.
                예: L = 10.0 m → 2π rad = 10.0 m → 1 rad ≈ 1.59 m
            각도:
                위상 2π [rad]가 전체 회전 360°에 대응됩니다.
                예: 2π rad = 360° → 1 rad ≈ 57.3°
        
        Args:
            phi_x: X 방향 위상 [0, 2π) [rad] (위치)
            phi_y: Y 방향 위상 [0, 2π) [rad] (위치)
            phi_z: Z 방향 위상 [0, 2π) [rad] (위치)
            phi_a: A 방향 위상 [0, 2π) [rad] (회전) ✨ NEW
            phi_b: B 방향 위상 [0, 2π) [rad] (회전) ✨ NEW
        
        Returns:
            (x, y, z, theta_a, theta_b)
                - x: X 방향 좌표 [m] (위치)
                - y: Y 방향 좌표 [m] (위치)
                - z: Z 방향 좌표 [m] (위치)
                - theta_a: A축 각도 [deg] (회전) ✨ NEW
                - theta_b: B축 각도 [deg] (회전) ✨ NEW
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 위치 변환: x = φx · (Lx / 2π)
        x = phi_x * (self.config.spatial_scale_x / self.config.phase_wrap)
        y = phi_y * (self.config.spatial_scale_y / self.config.phase_wrap)
        z = phi_z * (self.config.spatial_scale_z / self.config.phase_wrap)
        
        # 각도 변환: θa = φa · (180° / π) = φa · (360° / 2π)
        # ⚠️ 단위: phi_a, phi_b, phi_c는 [rad] (내부 단위)
        #          theta_a, theta_b, theta_c는 [deg] (출력 단위)
        #          math.degrees() 사용하여 명확한 변환
        import math
        theta_a = math.degrees(phi_a)  # rad → deg (명확한 변환)
        theta_b = math.degrees(phi_b)  # rad → deg (명확한 변환)
        theta_c = math.degrees(phi_c)  # rad → deg (명확한 변환)
        
        # angular_scale_a는 전체 회전 범위 (기본값 360°)
        # 주의: math.degrees()는 이미 2π rad = 360° 변환을 수행하므로
        #       추가 스케일링은 필요 없음 (필요시 나중에 추가 가능)
        
        return x, y, z, theta_a, theta_b, theta_c
    
    def coordinate_to_phase(
        self,
        x: float,
        y: float,
        z: float,
        theta_a: float,
        theta_b: float,
        theta_c: float  # C축 각도 [deg] (회전)
    ) -> Tuple[float, float, float, float, float, float]:
        """
        좌표/각도 → 위상 변환 (6D)
        
        외부 6D 좌표/각도(Coordinate/Angle)를 내부 위상(Phase)으로 변환합니다.
        외부 세계의 6D 위치/각도를 Grid 6D Engine의 내부 상태로 투영합니다.
        
        수학적 배경:
            phase_to_coordinate_6d()의 역변환입니다.
            좌표 (x, y, z) ∈ [0, L)³ → 위상 (φx, φy, φz) ∈ [0, 2π)³
            각도 (θa, θb) ∈ [0, 360°)² → 위상 (φa, φb) ∈ [0, 2π)²
        
        변환 수식 (위치):
            φx = x · (2π / Lx)
            φy = y · (2π / Ly)
            φz = z · (2π / Lz)
            
            여기서:
                - Lx = spatial_scale_x: X 방향 도메인 길이 [m]
                - Ly = spatial_scale_y: Y 방향 도메인 길이 [m]
                - Lz = spatial_scale_z: Z 방향 도메인 길이 [m]
                - 2π = phase_wrap: 위상 범위 [rad]
        
        변환 수식 (각도):
            φa = θa · (2π / 360°) = θa · (π / 180°)
            φb = θb · (2π / 360°) = θb · (π / 180°)
            
            여기서:
                - 360° = angular_scale_a: A축 각도 스케일 [deg] (전체 회전 범위)
                - 360° = angular_scale_b: B축 각도 스케일 [deg] (전체 회전 범위)
                - 2π = phase_wrap: 위상 범위 [rad]
        
        단위 분석:
            위치:
                φx [rad] = x [m] * (2π [rad] / Lx [m])
                φy [rad] = y [m] * (2π [rad] / Ly [m])
                φz [rad] = z [m] * (2π [rad] / Lz [m])
            각도:
                φa [rad] = θa [deg] * (2π [rad] / 360° [deg]) = θa [deg] * (π [rad] / 180° [deg])
                φb [rad] = θb [deg] * (2π [rad] / 360° [deg]) = θb [deg] * (π [rad] / 180° [deg])
        
        물리적 의미:
            위치:
                실제 공간 L [m]가 위상 2π [rad]에 대응됩니다.
                예: L = 10.0 m → 10.0 m = 2π rad → 1 m ≈ 0.628 rad
            각도:
                전체 회전 360°가 위상 2π [rad]에 대응됩니다.
                예: 360° = 2π rad → 1° ≈ 0.0175 rad
        
        Args:
            x: X 방향 좌표 [m] (위치)
            y: Y 방향 좌표 [m] (위치)
            z: Z 방향 좌표 [m] (위치)
            theta_a: A축 각도 [deg] (회전) ✨ NEW
            theta_b: B축 각도 [deg] (회전) ✨ NEW
        
        Returns:
            (phi_x, phi_y, phi_z, phi_a, phi_b) 위상 [rad]
                - phi_x: X 방향 위상 [rad] (정규화되지 않음)
                - phi_y: Y 방향 위상 [rad] (정규화되지 않음)
                - phi_z: Z 방향 위상 [rad] (정규화되지 않음)
                - phi_a: A 방향 위상 [rad] (정규화되지 않음) ✨ NEW
                - phi_b: B 방향 위상 [rad] (정규화되지 않음) ✨ NEW
        
        주의:
            반환된 위상은 [0, 2π) 범위를 벗어날 수 있습니다.
            normalize_phase()를 사용하여 정규화해야 합니다.
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        # 위치 변환: φx = x · (2π / Lx)
        phi_x = x * (self.config.phase_wrap / self.config.spatial_scale_x)
        phi_y = y * (self.config.phase_wrap / self.config.spatial_scale_y)
        phi_z = z * (self.config.phase_wrap / self.config.spatial_scale_z)
        
        # 각도 변환: φa = θa · (π / 180°)
        # ⚠️ 단위: theta_a, theta_b, theta_c는 [deg] (입력 단위)
        #          phi_a, phi_b, phi_c는 [rad] (내부 단위)
        #          math.radians() 사용하여 명확한 변환
        import math
        phi_a = math.radians(theta_a)  # deg → rad (명확한 변환)
        phi_b = math.radians(theta_b)  # deg → rad (명확한 변환)
        phi_c = math.radians(theta_c)  # deg → rad (명확한 변환)
        
        return phi_x, phi_y, phi_z, phi_a, phi_b, phi_c
    
    def project_state(self, state: Grid6DState) -> Tuple[float, float, float, float, float]:
        """
        상태의 위상을 6D 좌표/각도로 투영
        
        Args:
            state: Grid 6D 상태 (위상 포함)
        
        Returns:
            (x, y, z, theta_a, theta_b, theta_c) 좌표/각도
                - x, y, z: 위치 [m]
                - theta_a, theta_b, theta_c: 각도 [deg]
        """
        return self.phase_to_coordinate(
            state.phi_x, state.phi_y, state.phi_z, state.phi_a, state.phi_b, state.phi_c
        )


def create_projector_6d(config: Grid6DConfig) -> Coordinate6DProjector:
    """
    Coordinate6DProjector 생성
    
    Args:
        config: Grid 6D Engine 설정
    
    Returns:
        Coordinate6DProjector 인스턴스
    """
    return Coordinate6DProjector(config)


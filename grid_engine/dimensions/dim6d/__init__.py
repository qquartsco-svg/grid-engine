"""
Grid Engine 6D Module
6D Grid Engine 모듈 (6축 시스템)

6D 확장 (6축 시스템):
    - 2D: GridEngine (X, Y)
    - 3D: Grid3DEngine (X, Y, Z)
    - 4D: Grid4DEngine (X, Y, Z, W)
    - 6D: Grid6DEngine (X, Y, Z, A, B, C) ✨ NEW

핵심 구조:
    Grid 6D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ⊗ Ring C
    위상 공간: T⁶ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹
    
    6축 시스템 매핑:
        - 위치 축 (3개): X, Y, Z (선형 이동) [m]
        - 회전 축 (2개): A, B (각도 회전) [deg]

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (6D extension)
License: MIT License
"""

from .grid_6d_engine import Grid6DEngine
from .config_6d import Grid6DConfig
from .types_6d import Grid6DState, Grid6DInput, Grid6DOutput, Grid6DDiagnostics
from .projector_6d import Coordinate6DProjector

__all__ = [
    'Grid6DEngine',
    'Grid6DConfig',
    'Grid6DState',
    'Grid6DInput',
    'Grid6DOutput',
    'Grid6DDiagnostics',
    'Coordinate6DProjector',
]

__version__ = "0.4.0-alpha"


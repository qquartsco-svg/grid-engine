"""
Grid Engine 5D Module
5D Grid Engine 모듈 (5축 CNC)

5D 확장 (5축 CNC):
    - 2D: GridEngine (X, Y)
    - 3D: Grid3DEngine (X, Y, Z)
    - 4D: Grid4DEngine (X, Y, Z, W)
    - 5D: Grid5DEngine (X, Y, Z, A, B) ✨ NEW

핵심 구조:
    Grid 5D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B
    위상 공간: T⁵ = S¹ × S¹ × S¹ × S¹ × S¹
    
    5축 CNC 매핑:
        - 위치 축 (3개): X, Y, Z (선형 이동) [m]
        - 회전 축 (2개): A, B (각도 회전) [deg]

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

from .grid_5d_engine import Grid5DEngine
from .config_5d import Grid5DConfig
from .types_5d import Grid5DState, Grid5DInput, Grid5DOutput, Grid5DDiagnostics
from .projector_5d import Coordinate5DProjector

__all__ = [
    'Grid5DEngine',
    'Grid5DConfig',
    'Grid5DState',
    'Grid5DInput',
    'Grid5DOutput',
    'Grid5DDiagnostics',
    'Coordinate5DProjector',
]

__version__ = "0.4.0-alpha"


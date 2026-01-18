"""
Grid Engine 7D Module
7D Grid Engine 모듈 (7축 시스템)

7D 확장 (7축 시스템):
    - 2D: GridEngine (X, Y)
    - 3D: Grid3DEngine (X, Y, Z)
    - 4D: Grid4DEngine (X, Y, Z, W)
    - 7D: Grid7DEngine (X, Y, Z, A, B, C, D) ✨ NEW

핵심 구조:
    Grid 7D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ⊗ Ring C ⊗ Ring D
    위상 공간: T⁷ = S¹ × S¹ × S¹ × S¹ × S¹ × S¹ × S¹
    
    7축 시스템 매핑:
        - 위치 축 (3개): X, Y, Z (선형 이동) [m]
        - 회전 축 (2개): A, B (각도 회전) [deg]

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (7D extension)
License: MIT License
"""

from .grid_7d_engine import Grid7DEngine
from .config_7d import Grid7DConfig
from .types_7d import Grid7DState, Grid7DInput, Grid7DOutput, Grid7DDiagnostics
from .projector_7d import Coordinate7DProjector

__all__ = [
    'Grid7DEngine',
    'Grid7DConfig',
    'Grid7DState',
    'Grid7DInput',
    'Grid7DOutput',
    'Grid7DDiagnostics',
    'Coordinate7DProjector',
]

__version__ = "0.4.0-alpha"


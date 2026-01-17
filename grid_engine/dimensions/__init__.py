"""
Grid Engine Dimensions
차원별 모듈 (2D, 3D, 4D, ...)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha
License: MIT License
"""

# 편의를 위한 import
from .dim2d import Grid2DEngine, Grid2DConfig
from .dim3d import Grid3DEngine, Grid3DConfig
from .dim4d import Grid4DEngine, Grid4DConfig

__all__ = [
    'Grid2DEngine', 'Grid2DConfig',
    'Grid3DEngine', 'Grid3DConfig',
    'Grid4DEngine', 'Grid4DConfig',
]


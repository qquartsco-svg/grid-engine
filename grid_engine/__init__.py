"""
Grid Engine Package
차원별 Grid Engine 모듈 (2D, 3D, 4D, ...)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha
License: MIT License
"""

# 차원별 엔진 import
from .dimensions.dim2d import (
    Grid2DEngine, Grid2DConfig,
    GridState, GridInput, GridOutput, GridDiagnostics
)
from .dimensions.dim3d import Grid3DEngine, Grid3DConfig
from .dimensions.dim4d import Grid4DEngine, Grid4DConfig

# 공통 모듈 import
from .common.coupling import normalize_phase
from .common.energy import calculate_energy, compute_diagnostics

# 하위 호환성을 위한 별칭 (2D는 학습/개발용 기본)
# ⚠️ 주의: 로보틱스 프로젝트라면 Grid5DEngine을 사용하세요!
#   - 2D: 학습/개발용 기본 (가장 단순)
#   - 5D: 로보틱스 기본 (위치 3축 + 회전 2축) ⭐ 권장
#   - 6D: 산업 표준 (위치 3축 + 회전 3축)
#   - 7D: 초정밀/고급 (위치 3축 + 회전 4축)
GridEngine = Grid2DEngine  # 학습/개발용 기본
GridEngineConfig = Grid2DConfig  # 학습/개발용 기본

__all__ = [
    # 2D (기본)
    'GridEngine',  # 하위 호환성
    'GridEngineConfig',  # 하위 호환성
    'Grid2DEngine',
    'Grid2DConfig',
    'GridState',  # 2D 타입
    'GridInput',  # 2D 타입
    'GridOutput',  # 2D 타입
    'GridDiagnostics',  # 2D 타입
    # 3D
    'Grid3DEngine',
    'Grid3DConfig',
    # 4D
    'Grid4DEngine',
    'Grid4DConfig',
    # 공통
    'normalize_phase',
    'calculate_energy',
    'compute_diagnostics',
]

__version__ = "0.3.0-alpha"

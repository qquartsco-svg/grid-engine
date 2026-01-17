"""
Grid Engine
2D 위치 상태 유지 엔진

Ring ⊗ Ring 구조로 공간 위치를 안정적으로 유지

뉴턴 제2법칙 기반:
    Grid Engine은 뉴턴 제2법칙 (F = ma)을 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    상세 설명: docs/NEWTONS_LAW_CONNECTION.md 참조

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from .grid_engine import GridEngine
from .config import GridEngineConfig
from .types import GridState, GridInput, GridOutput, GridDiagnostics
from .coupling import normalize_phase, phase_to_coordinate, coordinate_to_phase
from .projector import CoordinateProjector

__version__ = "0.1.1"
__all__ = [
    "GridEngine",
    "GridEngineConfig",
    "GridState",
    "GridInput",
    "GridOutput",
    "GridDiagnostics",
    "normalize_phase",
    "phase_to_coordinate",
    "coordinate_to_phase",
    "CoordinateProjector",
]


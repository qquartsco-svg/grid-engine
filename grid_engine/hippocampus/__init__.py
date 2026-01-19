"""
Hippocampus Module
해마(Hippocampus) 구조 - 공간 기반 기억 시스템

구성 요소:
- Place Cells: 장소별 독립적인 기억
- Context Binder: 맥락별 기억 분리
- Learning Gate: 학습 조건 제어
- Replay/Consolidation: 기억 정제 및 장기 기억 고정
- Replay Buffer: 안정 구간 추출을 위한 버퍼

Author: GNJz
Created: 2026-01-20
Version: v0.4.0-alpha (Hippocampus Completion)
License: MIT License
"""

from .place_cells import PlaceMemory, PlaceCellManager
from .context_binder import ContextMemory, ContextBinder
from .learning_gate import LearningGateConfig, LearningGate
from .replay_consolidation import (
    PlaceMemoryWithHistory,
    ReplayConsolidation,
    ReplayConsolidationManager
)
from .replay_buffer import TrajectoryPoint, ReplayBuffer

__all__ = [
    # Place Cells
    'PlaceMemory',
    'PlaceCellManager',
    # Context Binder
    'ContextMemory',
    'ContextBinder',
    # Learning Gate
    'LearningGateConfig',
    'LearningGate',
    # Replay/Consolidation
    'PlaceMemoryWithHistory',
    'ReplayConsolidation',
    'ReplayConsolidationManager',
    # Replay Buffer
    'TrajectoryPoint',
    'ReplayBuffer',
]

__version__ = '0.4.0-alpha'


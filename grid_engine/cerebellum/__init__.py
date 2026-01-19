"""
Cerebellum Module
소뇌(Cerebellum) 구조 - 기억을 즉각 행동으로 변환하는 계층

구성 요소:
- Predictive Feedforward: 다음 순간의 오차 예측
- Trial-to-Trial 보정: 반복 궤적의 미세 편차 제거
- Variance 감소: 미세한 떨림 필터링
- 기억 기반 적응: 해마의 기억을 즉각 행동으로 변환

Author: GNJz
Created: 2026-01-20
Version: v0.5.0-alpha (Cerebellum Design)
License: MIT License
"""

from .cerebellum_engine import CerebellumEngine, CerebellumConfig, create_cerebellum_engine

__version__ = '0.5.0-alpha'

__all__ = [
    'CerebellumEngine',
    'CerebellumConfig',
    'create_cerebellum_engine',
]


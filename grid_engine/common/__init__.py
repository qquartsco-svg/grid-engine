"""
Grid Engine Common
공통 모듈 (coupling, energy, adapters)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha
License: MIT License
"""

from .coupling import normalize_phase
from .energy import calculate_energy, compute_diagnostics

__all__ = [
    'normalize_phase',
    'calculate_energy',
    'compute_diagnostics',
]


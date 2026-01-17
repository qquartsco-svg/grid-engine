"""
Grid Engine 초기화 테스트
"""

import pytest
from grid_engine import GridEngine, GridEngineConfig


def test_grid_engine_init_default():
    """기본 설정으로 초기화"""
    engine = GridEngine()
    state = engine.get_state()
    
    assert state.x == 0.0
    assert state.y == 0.0
    assert state.phi_x >= 0.0
    assert state.phi_y >= 0.0


def test_grid_engine_init_custom_position():
    """사용자 정의 위치로 초기화"""
    engine = GridEngine(initial_x=1.0, initial_y=2.0)
    state = engine.get_state()
    
    assert abs(state.x - 1.0) < 1e-6
    assert abs(state.y - 2.0) < 1e-6


def test_grid_engine_init_custom_config():
    """사용자 정의 설정으로 초기화"""
    config = GridEngineConfig(
        dt_ms=0.05,
        tau_ms=5.0,
        ring_size=20
    )
    engine = GridEngine(config=config)
    
    assert engine.config.dt_ms == 0.05
    assert engine.config.tau_ms == 5.0
    assert engine.config.ring_size == 20


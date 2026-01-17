"""
Grid Engine 경로 통합 테스트
"""

import pytest
from grid_engine import GridEngine, GridInput


def test_path_integration_velocity_only():
    """속도만으로 경로 통합"""
    engine = GridEngine()
    
    # 일정한 속도로 이동
    inp = GridInput(v_x=1.0, v_y=0.0)
    
    for _ in range(10):
        output = engine.step(inp)
    
    state = engine.get_state()
    assert state.x > 0.0  # X 방향으로 이동했어야 함
    assert abs(state.y) < 1e-6  # Y 방향은 변화 없음


def test_path_integration_with_acceleration():
    """가속도를 포함한 경로 통합"""
    engine = GridEngine()
    
    # 가속도 포함
    inp = GridInput(v_x=0.0, v_y=0.0, a_x=1.0, a_y=0.0)
    
    for _ in range(10):
        output = engine.step(inp)
    
    state = engine.get_state()
    assert state.x > 0.0  # 가속도로 인한 이동
    assert state.v_x > 0.0  # 속도 증가


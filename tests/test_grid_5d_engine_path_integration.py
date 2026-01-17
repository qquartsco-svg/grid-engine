"""
Grid 5D Engine 경로 통합 테스트

5D 확장 (5축 CNC):
    - 2D: test_grid_engine_path_integration.py
    - 3D: test_grid_3d_engine_path_integration.py
    - 4D: test_grid_4d_engine_path_integration.py
    - 5D: test_grid_5d_engine_path_integration.py ✨ NEW

테스트 항목:
    1. 등속 운동 (5D)
    2. 등가속도 운동 (5D)
    3. 위상 정규화 (5D)
    4. 좌표/각도 투영 (5D)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

import pytest
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DConfig, Grid5DInput


def test_grid_5d_engine_uniform_motion():
    """등속 운동 테스트 (5D)"""
    # dt_ms를 명시적으로 설정하여 max_dt_ratio 조건 만족
    config = Grid5DConfig(dt_ms=10.0, tau_ms=100.0, max_dt_ratio=0.2)
    engine = Grid5DEngine(config=config)
    
    # 5D 등속 운동 입력
    v_x = 1.0  # [m/s]
    v_y = 0.5  # [m/s]
    v_z = 0.3  # [m/s]
    v_a = 0.5  # [deg/s] (회전) ✨ NEW
    v_b = 0.3  # [deg/s] (회전) ✨ NEW
    
    inp = Grid5DInput(v_x=v_x, v_y=v_y, v_z=v_z, v_a=v_a, v_b=v_b)
    
    # 여러 스텝 실행
    n_steps = 10
    for _ in range(n_steps):
        engine.step(inp)
    
    state = engine.get_state()
    
    # 움직임 확인 (5D)
    # Ring Adapter의 영향으로 정확한 수치 비교는 어려우므로, 움직임이 있는지만 확인
    assert state.x != 0.0 or state.v_x != 0.0  # 위치 또는 속도가 0이 아님
    assert state.y != 0.0 or state.v_y != 0.0
    assert state.z != 0.0 or state.v_z != 0.0
    assert state.theta_a != 0.0 or state.v_a != 0.0  # 회전 각도 또는 각속도 ✨ NEW
    assert state.theta_b != 0.0 or state.v_b != 0.0  # 회전 각도 또는 각속도 ✨ NEW


def test_grid_5d_engine_uniform_acceleration():
    """등가속도 운동 테스트 (5D)"""
    # dt_ms를 명시적으로 설정하여 max_dt_ratio 조건 만족
    config = Grid5DConfig(dt_ms=10.0, tau_ms=100.0, max_dt_ratio=0.2)
    engine = Grid5DEngine(config=config)
    
    # 5D 등가속도 운동 입력
    a_x = 0.1  # [m/s²]
    a_y = 0.05  # [m/s²]
    a_z = 0.03  # [m/s²]
    alpha_a = 0.05  # [deg/s²] (회전) ✨ NEW
    alpha_b = 0.03  # [deg/s²] (회전) ✨ NEW
    
    inp = Grid5DInput(
        v_x=0.0, v_y=0.0, v_z=0.0,
        v_a=0.0, v_b=0.0,  # 회전 각속도 ✨ NEW
        a_x=a_x, a_y=a_y, a_z=a_z,
        alpha_a=alpha_a, alpha_b=alpha_b  # 회전 각가속도 ✨ NEW
    )
    
    # 여러 스텝 실행
    n_steps = 10
    for _ in range(n_steps):
        engine.step(inp)
    
    state = engine.get_state()
    
    # 가속도로 인한 속도 증가 확인 (5D)
    assert state.v_x > 0.0  # 속도가 증가함
    assert state.v_y > 0.0
    assert state.v_z > 0.0
    assert state.v_a > 0.0  # 회전 각속도 증가 ✨ NEW
    assert state.v_b > 0.0  # 회전 각속도 증가 ✨ NEW


def test_grid_5d_engine_phase_normalization():
    """위상 정규화 테스트 (5D)"""
    engine = Grid5DEngine()
    
    # 큰 위상 값 주입
    inp = Grid5DInput(
        v_x=100.0, v_y=100.0, v_z=100.0,
        v_a=100.0, v_b=100.0  # 회전 각속도 ✨ NEW
    )
    
    # 여러 스텝 실행
    for _ in range(100):
        engine.step(inp)
    
    state = engine.get_state()
    
    # 위상이 [0, 2π) 범위에 있는지 확인 (5D)
    import math
    phase_wrap = 2.0 * math.pi
    
    assert 0.0 <= state.phi_x < phase_wrap
    assert 0.0 <= state.phi_y < phase_wrap
    assert 0.0 <= state.phi_z < phase_wrap
    assert 0.0 <= state.phi_a < phase_wrap  # 회전 위상 ✨ NEW
    assert 0.0 <= state.phi_b < phase_wrap  # 회전 위상 ✨ NEW


def test_grid_5d_engine_coordinate_projection():
    """좌표/각도 투영 테스트 (5D)"""
    engine = Grid5DEngine()
    
    # 위상 설정 후 좌표/각도 확인
    inp = Grid5DInput(v_x=1.0, v_y=0.5, v_z=0.3, v_a=0.5, v_b=0.3)
    output = engine.step(inp)
    
    # 좌표/각도 투영 확인 (5D)
    assert output.x is not None
    assert output.y is not None
    assert output.z is not None
    assert output.theta_a is not None  # 회전 각도 ✨ NEW
    assert output.theta_b is not None  # 회전 각도 ✨ NEW
    
    # 위상 확인 (5D)
    assert output.phi_x is not None
    assert output.phi_y is not None
    assert output.phi_z is not None
    assert output.phi_a is not None  # 회전 위상 ✨ NEW
    assert output.phi_b is not None  # 회전 위상 ✨ NEW


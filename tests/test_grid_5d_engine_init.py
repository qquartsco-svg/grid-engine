"""
Grid 5D Engine 초기화 테스트

5D 확장 (5축 CNC):
    - 2D: test_grid_engine_init.py
    - 3D: test_grid_3d_engine_init.py
    - 4D: test_grid_4d_engine_init.py
    - 5D: test_grid_5d_engine_init.py ✨ NEW

테스트 항목:
    1. 기본 초기화 (5D)
    2. 사용자 정의 초기화 (5D)
    3. Config 초기화 (5D)
    4. 초기 step 실행 (5D)
    5. 리셋 기능 (5D)

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


def test_grid_5d_engine_default_init():
    """기본 초기화 테스트 (5D)"""
    engine = Grid5DEngine()
    state = engine.get_state()
    
    # 기본 상태 확인 (5D)
    assert state.phi_x == 0.0
    assert state.phi_y == 0.0
    assert state.phi_z == 0.0
    assert state.phi_a == 0.0  # 회전 위상 ✨ NEW
    assert state.phi_b == 0.0  # 회전 위상 ✨ NEW
    
    assert state.x == 0.0
    assert state.y == 0.0
    assert state.z == 0.0
    assert state.theta_a == 0.0  # 회전 각도 ✨ NEW
    assert state.theta_b == 0.0  # 회전 각도 ✨ NEW
    
    assert state.v_x == 0.0
    assert state.v_y == 0.0
    assert state.v_z == 0.0
    assert state.v_a == 0.0  # 회전 각속도 ✨ NEW
    assert state.v_b == 0.0  # 회전 각속도 ✨ NEW


def test_grid_5d_engine_custom_init():
    """사용자 정의 초기화 테스트 (5D)"""
    initial_x = 1.0
    initial_y = 2.0
    initial_z = 3.0
    initial_theta_a = 45.0  # 회전 각도 [deg] ✨ NEW
    initial_theta_b = 90.0  # 회전 각도 [deg] ✨ NEW
    
    engine = Grid5DEngine(
        initial_x=initial_x,
        initial_y=initial_y,
        initial_z=initial_z,
        initial_theta_a=initial_theta_a,
        initial_theta_b=initial_theta_b
    )
    state = engine.get_state()
    
    # 초기 좌표/각도 확인 (5D)
    assert abs(state.x - initial_x) < 1e-6
    assert abs(state.y - initial_y) < 1e-6
    assert abs(state.z - initial_z) < 1e-6
    assert abs(state.theta_a - initial_theta_a) < 1e-6  # 회전 각도 ✨ NEW
    assert abs(state.theta_b - initial_theta_b) < 1e-6  # 회전 각도 ✨ NEW


def test_grid_5d_engine_config_init():
    """Config 초기화 테스트 (5D)"""
    config = Grid5DConfig(
        spatial_scale_x=10.0,
        spatial_scale_y=10.0,
        spatial_scale_z=10.0,
        angular_scale_a=360.0,  # 회전 축 ✨ NEW
        angular_scale_b=360.0,  # 회전 축 ✨ NEW
        dt_ms=1.0,
        max_dt_ratio=0.2
    )
    
    engine = Grid5DEngine(config=config)
    state = engine.get_state()
    
    # Config가 적용되었는지 확인
    assert engine.config.spatial_scale_x == 10.0
    assert engine.config.spatial_scale_y == 10.0
    assert engine.config.spatial_scale_z == 10.0
    assert engine.config.angular_scale_a == 360.0  # 회전 축 ✨ NEW
    assert engine.config.angular_scale_b == 360.0  # 회전 축 ✨ NEW


def test_grid_5d_engine_step_initial():
    """초기 step 실행 테스트 (5D)"""
    engine = Grid5DEngine()
    
    # 5D 입력 생성
    inp = Grid5DInput(
        v_x=1.0, v_y=0.5, v_z=0.3,
        v_a=0.5, v_b=0.3  # 회전 각속도 [deg/s] ✨ NEW
    )
    
    output = engine.step(inp)
    state = engine.get_state()
    
    # 출력 확인 (5D)
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


def test_grid_5d_engine_reset():
    """리셋 기능 테스트 (5D)"""
    engine = Grid5DEngine()
    
    # 이동 후 리셋
    inp = Grid5DInput(v_x=1.0, v_y=0.5, v_z=0.3, v_a=0.5, v_b=0.3)
    engine.step(inp)
    
    # 리셋 (5D)
    engine.reset(x=0.0, y=0.0, z=0.0, theta_a=0.0, theta_b=0.0)
    state = engine.get_state()
    
    # 리셋 확인 (5D)
    assert abs(state.x) < 1e-6
    assert abs(state.y) < 1e-6
    assert abs(state.z) < 1e-6
    assert abs(state.theta_a) < 1e-6  # 회전 각도 ✨ NEW
    assert abs(state.theta_b) < 1e-6  # 회전 각도 ✨ NEW


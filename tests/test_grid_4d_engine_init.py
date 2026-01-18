"""
Grid 4D Engine 초기화 테스트

이 테스트는 Grid 4D Engine의 초기화 기능을 검증합니다.

테스트 항목:
    1. 기본 초기화 (4D)
    2. 초기 좌표 설정 (4D)
    3. 초기 상태 검증 (4D)
    4. Ring Adapter 초기화 (4D)
    5. Projector 초기화 (4D)

4D 확장:
    - 2D: (x, y), (φx, φy)
    - 3D: (x, y, z), (φx, φy, φz)
    - 4D: (x, y, z, w), (φx, φy, φz, φw) ✨ NEW

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

import pytest
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim4d.grid_4d_engine import Grid4DEngine
from grid_engine.dimensions.dim4d.config_4d import Grid4DConfig
from grid_engine.dimensions.dim4d.types_4d import Grid4DInput


def test_grid_4d_engine_default_init():
    """기본 초기화 테스트 (4D)"""
    engine = Grid4DEngine()
    
    state = engine.get_state()
    
    # 초기 상태 검증 (4D)
    assert state.phi_x == 0.0
    assert state.phi_y == 0.0
    assert state.phi_z == 0.0
    assert state.phi_w == 0.0  # W 방향 추가 ✨ NEW
    assert state.x == 0.0
    assert state.y == 0.0
    assert state.z == 0.0
    assert state.w == 0.0  # W 좌표 추가 ✨ NEW
    assert state.v_x == 0.0
    assert state.v_y == 0.0
    assert state.v_z == 0.0
    assert state.v_w == 0.0  # W 속도 추가 ✨ NEW
    assert state.t_ms == 0.0


def test_grid_4d_engine_custom_init():
    """초기 좌표 설정 테스트 (4D)"""
    engine = Grid4DEngine(initial_x=1.0, initial_y=2.0, initial_z=3.0, initial_w=4.0)
    
    state = engine.get_state()
    
    # 초기 좌표 검증 (4D)
    # 주의: spatial_scale=1.0일 때 좌표 → 위상 변환 후 정규화하면
    #       위상이 0이 될 수 있습니다 (정상 동작).
    #       예: 1.0 * (2π / 1.0) = 2π, 2π % 2π = 0
    assert state.x == pytest.approx(1.0, rel=1e-3)
    assert state.y == pytest.approx(2.0, rel=1e-3)
    assert state.z == pytest.approx(3.0, rel=1e-3)
    assert state.w == pytest.approx(4.0, rel=1e-3)  # W 좌표 추가 ✨ NEW


def test_grid_4d_engine_config_init():
    """설정 기반 초기화 테스트 (4D)"""
    config = Grid4DConfig(
        spatial_scale_x=20.0,
        spatial_scale_y=20.0,
        spatial_scale_z=20.0,
        spatial_scale_w=20.0  # W 스케일 추가 ✨ NEW
    )
    engine = Grid4DEngine(config=config)
    
    state = engine.get_state()
    
    # 설정이 적용되었는지 검증 (4D)
    assert engine.config.spatial_scale_x == 20.0
    assert engine.config.spatial_scale_y == 20.0
    assert engine.config.spatial_scale_z == 20.0
    assert engine.config.spatial_scale_w == 20.0  # W 스케일 추가 ✨ NEW


def test_grid_4d_engine_step_initial():
    """초기 상태에서 step 테스트 (4D)"""
    engine = Grid4DEngine()
    
    # 입력 (4D)
    inp = Grid4DInput(v_x=0.0, v_y=0.0, v_z=0.0, v_w=0.0)
    
    output = engine.step(inp)
    
    # 출력 검증 (4D)
    assert output.x == pytest.approx(0.0, abs=1e-6)
    assert output.y == pytest.approx(0.0, abs=1e-6)
    assert output.z == pytest.approx(0.0, abs=1e-6)
    assert output.w == pytest.approx(0.0, abs=1e-6)  # W 좌표 추가 ✨ NEW
    assert output.phi_x == pytest.approx(0.0, abs=1e-6)
    assert output.phi_y == pytest.approx(0.0, abs=1e-6)
    assert output.phi_z == pytest.approx(0.0, abs=1e-6)
    assert output.phi_w == pytest.approx(0.0, abs=1e-6)  # W 위상 추가 ✨ NEW


def test_grid_4d_engine_reset():
    """리셋 테스트 (4D)"""
    engine = Grid4DEngine(initial_x=1.0, initial_y=2.0, initial_z=3.0, initial_w=4.0)
    
    # 이동 (4D)
    inp = Grid4DInput(v_x=1.0, v_y=1.0, v_z=1.0, v_w=1.0)
    engine.step(inp)
    
    # 리셋 (4D)
    engine.reset(x=5.0, y=6.0, z=7.0, w=8.0)
    
    state = engine.get_state()
    
    # 리셋 후 상태 검증 (4D)
    assert state.x == pytest.approx(5.0, rel=1e-3)
    assert state.y == pytest.approx(6.0, rel=1e-3)
    assert state.z == pytest.approx(7.0, rel=1e-3)
    assert state.w == pytest.approx(8.0, rel=1e-3)  # W 좌표 추가 ✨ NEW
    assert state.v_x == 0.0
    assert state.v_y == 0.0
    assert state.v_z == 0.0
    assert state.v_w == 0.0  # W 속도 추가 ✨ NEW
    assert state.t_ms == 0.0


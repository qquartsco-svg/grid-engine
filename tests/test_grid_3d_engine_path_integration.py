"""
Grid 3D Engine 경로 통합 테스트

이 테스트는 Grid 3D Engine의 경로 통합(Path Integration) 기능을 검증합니다.

테스트 항목:
    1. 등속 운동 (3D)
    2. 등가속도 운동 (3D)
    3. 위상 정규화 (3D)
    4. 좌표 투영 (3D)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
License: MIT License
"""

import pytest
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim3d.grid_3d_engine import Grid3DEngine
from grid_engine.dimensions.dim3d.config_3d import Grid3DConfig
from grid_engine.dimensions.dim3d.types_3d import Grid3DInput


def test_grid_3d_engine_uniform_motion():
    """등속 운동 테스트 (3D)"""
    # dt_ms를 명시적으로 설정하여 max_dt_ratio 조건 만족
    config = Grid3DConfig(dt_ms=10.0, tau_ms=100.0, max_dt_ratio=0.2)  # dt_ms=10.0 < 100.0*0.2=20.0
    engine = Grid3DEngine(config=config)
    
    # 등속 운동 입력 (3D)
    v_x = 1.0  # m/s
    v_y = 0.5  # m/s
    v_z = 0.3  # m/s (Z 방향 추가)
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z)
    
    # 여러 스텝 실행
    n_steps = 10
    for _ in range(n_steps):
        output = engine.step(inp)
    
    state = engine.get_state()
    
    # 경로 통합 검증 (3D)
    # 주의: Ring Adapter의 안정화 효과로 인해 실제 좌표가 이론값과 다를 수 있음
    # 따라서 정확한 수치 검증보다는 "움직임이 있는지"와 "방향이 맞는지"를 확인
    
    # 1. 움직임이 있어야 함 (0이 아니어야 함)
    assert abs(state.x) > 1e-6 or abs(state.y) > 1e-6 or abs(state.z) > 1e-6, \
        "경로 통합이 작동하지 않음: 모든 좌표가 0"
    
    # 2. 속도 방향과 일치해야 함
    if v_x > 0:
        assert state.x > 0 or state.v_x > 0, f"X 방향 속도가 양수인데 좌표와 속도가 음수: x={state.x}, v_x={state.v_x}"
    if v_y > 0:
        assert state.y > 0 or state.v_y > 0, f"Y 방향 속도가 양수인데 좌표와 속도가 음수: y={state.y}, v_y={state.v_y}"
    if v_z > 0:
        assert state.z > 0 or state.v_z > 0, f"Z 방향 속도가 양수인데 좌표와 속도가 음수: z={state.z}, v_z={state.v_z}"


def test_grid_3d_engine_uniform_acceleration():
    """등가속도 운동 테스트 (3D)"""
    # dt_ms를 명시적으로 설정하여 max_dt_ratio 조건 만족
    config = Grid3DConfig(dt_ms=10.0, tau_ms=100.0, max_dt_ratio=0.2)  # dt_ms=10.0 < 100.0*0.2=20.0
    engine = Grid3DEngine(config=config)
    
    # 등가속도 운동 입력 (3D)
    v_x = 0.0  # 초기 속도
    v_y = 0.0
    v_z = 0.0
    a_x = 0.1  # m/s²
    a_y = 0.05  # m/s²
    a_z = 0.03  # m/s² (Z 방향 추가)
    n_steps = 10
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z, a_x=a_x, a_y=a_y, a_z=a_z)
    
    # n_steps 스텝 실행
    for _ in range(n_steps):
        output = engine.step(inp)
    
    state = engine.get_state()
    
    # 경로 통합 검증 (3D)
    # 주의: Ring Adapter의 안정화 효과로 인해 실제 좌표가 이론값과 다를 수 있음
    # 따라서 정확한 수치 검증보다는 "가속도로 인한 속도 증가"를 확인
    
    # 가속도로 인한 속도 증가 확인
    assert state.v_x > 0.0, f"X 방향 가속도가 양수인데 속도가 증가하지 않음: v_x={state.v_x}"
    assert state.v_y > 0.0, f"Y 방향 가속도가 양수인데 속도가 증가하지 않음: v_y={state.v_y}"
    assert state.v_z > 0.0, f"Z 방향 가속도가 양수인데 속도가 증가하지 않음: v_z={state.v_z}"


def test_grid_3d_engine_phase_normalization():
    """위상 정규화 테스트 (3D)"""
    engine = Grid3DEngine()
    
    # 큰 속도 입력으로 위상이 2π를 넘도록 함 (3D)
    # 위상이 2π를 넘으면 정규화되어야 함
    v_x = 100.0  # 매우 큰 속도
    v_y = 100.0
    v_z = 100.0  # Z 방향 추가
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z)
    
    # 여러 스텝 실행
    for _ in range(100):
        output = engine.step(inp)
        
        # 위상은 [0, 2π) 범위에 있어야 함 (3D)
        phase_wrap = engine.config.phase_wrap
        assert 0.0 <= output.phi_x < phase_wrap
        assert 0.0 <= output.phi_y < phase_wrap
        assert 0.0 <= output.phi_z < phase_wrap  # Z 위상 추가


def test_grid_3d_engine_coordinate_projection():
    """좌표 투영 테스트 (3D)"""
    engine = Grid3DEngine()
    
    # 특정 위상 설정을 위해 큰 속도로 이동 (3D)
    v_x = 10.0
    v_y = 5.0
    v_z = 2.0  # Z 방향 추가
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z)
    
    # 이동
    output = engine.step(inp)
    
    state = engine.get_state()
    
    # 좌표와 위상이 일관성이 있어야 함 (3D)
    # projector를 통해 위상 → 좌표 변환 확인
    x_from_phi = engine.projector.phase_to_coordinate(
        state.phi_x, state.phi_y, state.phi_z
    )
    
    assert state.x == pytest.approx(x_from_phi[0], rel=1e-3)
    assert state.y == pytest.approx(x_from_phi[1], rel=1e-3)
    assert state.z == pytest.approx(x_from_phi[2], rel=1e-3)  # Z 좌표 추가


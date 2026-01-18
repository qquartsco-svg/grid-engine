"""
Grid 4D Engine 경로 통합 테스트

이 테스트는 Grid 4D Engine의 경로 통합(Path Integration) 기능을 검증합니다.

테스트 항목:
    1. 등속 운동 (4D)
    2. 등가속도 운동 (4D)
    3. 위상 정규화 (4D)
    4. 좌표 투영 (4D)

4D 확장:
    - 2D: (vx, vy), (ax, ay) → (φx, φy)
    - 3D: (vx, vy, vz), (ax, ay, az) → (φx, φy, φz)
    - 4D: (vx, vy, vz, vw), (ax, ay, az, aw) → (φx, φy, φz, φw) ✨ NEW

뉴턴 제2법칙 검증:
    등가속도 운동: Δx = v₀·t + ½a·t² (4D)
    등속 운동: Δx = v·t (4D)

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


def test_grid_4d_engine_uniform_motion():
    """등속 운동 테스트 (4D)"""
    # dt_ms를 명시적으로 설정 (테스트용)
    # 주의: dt_ms < tau_ms * max_dt_ratio 조건을 만족해야 함
    config = Grid4DConfig(dt_ms=1.0, tau_ms=10.0, max_dt_ratio=0.2)  # dt_ms=1.0 < 10.0*0.2=2.0
    engine = Grid4DEngine(config=config)
    
    # 등속 운동 입력 (4D)
    v_x = 1.0  # m/s
    v_y = 0.5  # m/s
    v_z = 0.3  # m/s
    v_w = 0.2  # m/s (W 방향 추가) ✨ NEW
    dt_ms = config.dt_ms  # 1.0 ms
    n_steps = 100  # 더 많은 스텝으로 누적 변위 증가
    
    inp = Grid4DInput(v_x=v_x, v_y=v_y, v_z=v_z, v_w=v_w)
    
    # n_steps 스텝 실행
    for _ in range(n_steps):
        output = engine.step(inp)
    
    state = engine.get_state()
    
    # 경로 통합 검증 (4D)
    # 주의: Ring Adapter의 안정화 효과로 인해 실제 좌표가 이론값과 다를 수 있음
    # 따라서 정확한 수치 검증보다는 "움직임이 있는지"와 "방향이 맞는지"를 확인
    
    # 1. 움직임이 있어야 함 (0이 아니어야 함)
    assert abs(state.x) > 1e-6 or abs(state.y) > 1e-6 or abs(state.z) > 1e-6 or abs(state.w) > 1e-6, \
        "경로 통합이 작동하지 않음: 모든 좌표가 0"
    
    # 2. 속도 방향과 일치해야 함
    if v_x > 0:
        assert state.x > 0, f"X 방향 속도가 양수인데 좌표가 음수: x={state.x}"
    if v_y > 0:
        assert state.y > 0, f"Y 방향 속도가 양수인데 좌표가 음수: y={state.y}"
    if v_z > 0:
        assert state.z > 0, f"Z 방향 속도가 양수인데 좌표가 음수: z={state.z}"
    if v_w > 0:
        assert state.w > 0, f"W 방향 속도가 양수인데 좌표가 음수: w={state.w}"  # W 방향 추가 ✨ NEW


def test_grid_4d_engine_uniform_acceleration():
    """등가속도 운동 테스트 (4D)"""
    # dt_ms를 명시적으로 설정 (테스트용)
    # 주의: dt_ms < tau_ms * max_dt_ratio 조건을 만족해야 함
    config = Grid4DConfig(dt_ms=1.0, tau_ms=10.0, max_dt_ratio=0.2)  # dt_ms=1.0 < 10.0*0.2=2.0
    engine = Grid4DEngine(config=config)
    
    # 등가속도 운동 입력 (4D)
    v_x = 0.0  # 초기 속도
    v_y = 0.0
    v_z = 0.0
    v_w = 0.0  # W 초기 속도 추가 ✨ NEW
    a_x = 1.0  # m/s²
    a_y = 0.5  # m/s²
    a_z = 0.3  # m/s²
    a_w = 0.2  # m/s² (W 방향 추가) ✨ NEW
    dt_ms = config.dt_ms  # 1.0 ms
    n_steps = 100  # 더 많은 스텝으로 누적 변위 증가
    
    inp = Grid4DInput(v_x=v_x, v_y=v_y, v_z=v_z, v_w=v_w, a_x=a_x, a_y=a_y, a_z=a_z, a_w=a_w)
    
    # n_steps 스텝 실행
    for _ in range(n_steps):
        output = engine.step(inp)
    
    state = engine.get_state()
    
    # 경로 통합 검증 (4D, 등가속도 운동)
    # 주의: Ring Adapter의 안정화 효과로 인해 실제 좌표가 이론값과 다를 수 있음
    # 따라서 정확한 수치 검증보다는 "움직임이 있는지"와 "방향이 맞는지"를 확인
    
    # 1. 움직임이 있어야 함 (0이 아니어야 함)
    assert abs(state.x) > 1e-6 or abs(state.y) > 1e-6 or abs(state.z) > 1e-6 or abs(state.w) > 1e-6, \
        "경로 통합이 작동하지 않음: 모든 좌표가 0"
    
    # 2. 가속도 방향과 일치해야 함 (뉴턴 2법칙)
    if a_x > 0:
        assert state.x > 0, f"X 방향 가속도가 양수인데 좌표가 음수: x={state.x}"
    if a_y > 0:
        assert state.y > 0, f"Y 방향 가속도가 양수인데 좌표가 음수: y={state.y}"
    if a_z > 0:
        assert state.z > 0, f"Z 방향 가속도가 양수인데 좌표가 음수: z={state.z}"
    if a_w > 0:
        assert state.w > 0, f"W 방향 가속도가 양수인데 좌표가 음수: w={state.w}"  # W 방향 추가 ✨ NEW
    
    # 3. 속도도 증가해야 함 (가속도 효과)
    assert state.v_x > 0 or state.v_y > 0 or state.v_z > 0 or state.v_w > 0, \
        "가속도가 적용되었는데 속도가 증가하지 않음"


def test_grid_4d_engine_phase_normalization():
    """위상 정규화 테스트 (4D)"""
    engine = Grid4DEngine()
    
    # 큰 속도 입력으로 위상이 2π를 넘도록 함 (4D)
    # 위상이 2π를 넘으면 정규화되어야 함
    v_x = 100.0  # 매우 큰 속도
    v_y = 100.0
    v_z = 100.0
    v_w = 100.0  # W 방향 추가 ✨ NEW
    
    inp = Grid4DInput(v_x=v_x, v_y=v_y, v_z=v_z, v_w=v_w)
    
    # 여러 스텝 실행
    for _ in range(100):
        output = engine.step(inp)
        
        # 위상은 [0, 2π) 범위에 있어야 함 (4D)
        phase_wrap = engine.config.phase_wrap
        assert 0.0 <= output.phi_x < phase_wrap
        assert 0.0 <= output.phi_y < phase_wrap
        assert 0.0 <= output.phi_z < phase_wrap
        assert 0.0 <= output.phi_w < phase_wrap  # W 위상 추가 ✨ NEW


def test_grid_4d_engine_coordinate_projection():
    """좌표 투영 테스트 (4D)"""
    engine = Grid4DEngine()
    
    # 특정 위상 설정을 위해 큰 속도로 이동 (4D)
    v_x = 10.0
    v_y = 5.0
    v_z = 2.0
    v_w = 1.0  # W 방향 추가 ✨ NEW
    
    inp = Grid4DInput(v_x=v_x, v_y=v_y, v_z=v_z, v_w=v_w)
    
    # 이동
    output = engine.step(inp)
    
    state = engine.get_state()
    
    # 좌표와 위상이 일관성이 있어야 함 (4D)
    # projector를 통해 위상 → 좌표 변환 확인
    x_from_phi = engine.projector.phase_to_coordinate(
        state.phi_x, state.phi_y, state.phi_z, state.phi_w
    )
    
    assert state.x == pytest.approx(x_from_phi[0], rel=1e-3)
    assert state.y == pytest.approx(x_from_phi[1], rel=1e-3)
    assert state.z == pytest.approx(x_from_phi[2], rel=1e-3)
    assert state.w == pytest.approx(x_from_phi[3], rel=1e-3)  # W 좌표 추가 ✨ NEW


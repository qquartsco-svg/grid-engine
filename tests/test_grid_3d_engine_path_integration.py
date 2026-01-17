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
from grid_engine.dimensions.dim3d.grid_3d_engine import Grid3DEngine
from grid_engine.dimensions.dim3d.types_3d import Grid3DInput


def test_grid_3d_engine_uniform_motion():
    """등속 운동 테스트 (3D)"""
    engine = Grid3DEngine()
    
    # 등속 운동 입력 (3D)
    v_x = 1.0  # m/s
    v_y = 0.5  # m/s
    v_z = 0.3  # m/s (Z 방향 추가)
    dt_ms = 100.0  # ms = 0.1 s
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z)
    
    # 10 스텝 실행
    for _ in range(10):
        output = engine.step(inp)
    
    state = engine.get_state()
    
    # 경로 통합 검증 (3D)
    # 예상 변위: Δx = v · Δt = 1.0 * 0.1 * 10 = 1.0 m
    expected_x = v_x * (dt_ms / 1000.0) * 10
    expected_y = v_y * (dt_ms / 1000.0) * 10
    expected_z = v_z * (dt_ms / 1000.0) * 10  # Z 방향 추가
    
    assert state.x == pytest.approx(expected_x, rel=0.1)
    assert state.y == pytest.approx(expected_y, rel=0.1)
    assert state.z == pytest.approx(expected_z, rel=0.1)  # Z 좌표 추가


def test_grid_3d_engine_uniform_acceleration():
    """등가속도 운동 테스트 (3D)"""
    engine = Grid3DEngine()
    
    # 등가속도 운동 입력 (3D)
    v_x = 0.0  # 초기 속도
    v_y = 0.0
    v_z = 0.0
    a_x = 1.0  # m/s²
    a_y = 0.5  # m/s²
    a_z = 0.3  # m/s² (Z 방향 추가)
    dt_ms = 100.0  # ms = 0.1 s
    n_steps = 10
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z, a_x=a_x, a_y=a_y, a_z=a_z)
    
    # n_steps 스텝 실행
    for _ in range(n_steps):
        output = engine.step(inp)
    
    state = engine.get_state()
    
    # 경로 통합 검증 (3D)
    # 수식: Δx = v₀·t + ½a·t²
    dt_s = dt_ms / 1000.0
    total_t = dt_s * n_steps
    
    expected_x = 0.5 * a_x * (total_t ** 2)
    expected_y = 0.5 * a_y * (total_t ** 2)
    expected_z = 0.5 * a_z * (total_t ** 2)  # Z 방향 추가
    
    assert state.x == pytest.approx(expected_x, rel=0.2)
    assert state.y == pytest.approx(expected_y, rel=0.2)
    assert state.z == pytest.approx(expected_z, rel=0.2)  # Z 좌표 추가


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


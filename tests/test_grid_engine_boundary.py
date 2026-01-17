"""
Grid Engine 경계 조건 테스트
위상 주기성 및 경계 처리 검증

Author: [작성자 시그니처]
Created: 2026-01
"""

import pytest
import numpy as np
from grid_engine import GridEngine, GridInput, GridEngineConfig
from grid_engine.coupling import normalize_phase


def test_phase_wrap_boundary():
    """위상 주기적 경계 조건 테스트"""
    engine = GridEngine()
    config = engine.config
    
    # 위상이 2π를 넘어가는 경우
    # 위상이 주기적으로 감싸지는지 확인
    phase_wrap = config.phase_wrap  # 2π
    
    # 위상을 직접 설정하여 경계 테스트
    # 주의: GridState는 내부적으로 정규화하지만,
    # coupling.normalize_phase()가 올바르게 작동하는지 확인
    phi_test = phase_wrap + 0.5  # 2π + 0.5
    phi_norm = normalize_phase(phi_test, phase_wrap)
    
    # 정규화된 위상은 [0, 2π) 범위에 있어야 함
    assert 0.0 <= phi_norm < phase_wrap
    assert abs(phi_norm - 0.5) < 1e-6  # 2π + 0.5 ≡ 0.5 (mod 2π)


def test_phase_negative_wrap():
    """음수 위상 경계 조건 테스트"""
    engine = GridEngine()
    config = engine.config
    phase_wrap = config.phase_wrap  # 2π
    
    # 음수 위상 테스트
    phi_test = -0.5  # -0.5
    phi_norm = normalize_phase(phi_test, phase_wrap)
    
    # 정규화된 위상은 [0, 2π) 범위에 있어야 함
    assert 0.0 <= phi_norm < phase_wrap
    # -0.5 ≡ 2π - 0.5 (mod 2π)
    expected = phase_wrap - 0.5
    assert abs(phi_norm - expected) < 1e-6


def test_large_phase_wrap():
    """큰 위상 값의 주기적 감싸기 테스트"""
    engine = GridEngine()
    config = engine.config
    phase_wrap = config.phase_wrap  # 2π
    
    # 큰 위상 값 테스트 (10π)
    phi_test = 10.0 * np.pi
    phi_norm = normalize_phase(phi_test, phase_wrap)
    
    # 정규화된 위상은 [0, 2π) 범위에 있어야 함
    assert 0.0 <= phi_norm < phase_wrap
    
    # 10π mod 2π = 0 (10은 2의 배수이므로)
    assert abs(phi_norm) < 1e-6


def test_coordinate_phase_consistency():
    """좌표 ↔ 위상 변환 일관성 테스트"""
    engine = GridEngine()
    projector = engine.projector
    config = engine.config
    
    # 테스트 좌표 (도메인 길이 내에서)
    # 주의: 좌표가 spatial_scale보다 작아야 정규화 후에도 일관성 유지
    # spatial_scale_x = 1.0 [m]이므로 0.5 [m] 정도로 테스트
    test_x = 0.3  # [m] (< spatial_scale_x = 1.0)
    test_y = 0.2  # [m] (< spatial_scale_y = 1.0)
    
    # 좌표 → 위상 변환
    phi_x, phi_y = projector.coordinate_to_phase(test_x, test_y)
    
    # 위상 → 좌표 역변환 (정규화 없이)
    x_back, y_back = projector.phase_to_coordinate(phi_x, phi_y)
    
    # 직접 변환은 일치해야 함 (정규화 전)
    assert abs(x_back - test_x) < 1e-6
    assert abs(y_back - test_y) < 1e-6
    
    # 위상 정규화 후 변환 테스트
    phi_x_norm = normalize_phase(phi_x, config.phase_wrap)
    phi_y_norm = normalize_phase(phi_y, config.phase_wrap)
    
    x_from_norm, y_from_norm = projector.phase_to_coordinate(phi_x_norm, phi_y_norm)
    
    # 정규화된 위상으로부터 복원된 좌표는 원래 좌표와 일치해야 함
    # (도메인 길이 내에서만 성립)
    assert abs(x_from_norm - test_x) < 1e-6
    assert abs(y_from_norm - test_y) < 1e-6


def test_phase_wrap_in_step():
    """step 함수에서 위상 주기성 유지 확인"""
    engine = GridEngine()
    
    # 매우 큰 속도로 여러 스텝 실행
    # 위상이 2π를 넘어가도 주기적으로 감싸지는지 확인
    inp = GridInput(v_x=1000.0, v_y=0.0)  # 매우 큰 속도
    
    for _ in range(100):
        output = engine.step(inp)
        state = engine.get_state()
        
        # 위상이 [0, 2π) 범위에 있어야 함
        phase_wrap = engine.config.phase_wrap
        assert 0.0 <= state.phi_x < phase_wrap
        assert 0.0 <= state.phi_y < phase_wrap


def test_spatial_scale_independence():
    """공간 스케일 변경 시 위상 정규화 일관성"""
    # 다른 공간 스케일로 엔진 생성
    config_small = GridEngineConfig(spatial_scale_x=1.0, spatial_scale_y=1.0)
    config_large = GridEngineConfig(spatial_scale_x=10.0, spatial_scale_y=10.0)
    
    engine_small = GridEngine(config=config_small)
    engine_large = GridEngine(config=config_large)
    
    # 같은 위상으로 설정
    test_phi_x = 1.0  # [rad]
    test_phi_y = 2.0  # [rad]
    
    # 위상을 직접 설정할 수 없으므로,
    # 좌표를 통해 위상 설정
    x_small = test_phi_x * (config_small.spatial_scale_x / config_small.phase_wrap)
    y_small = test_phi_y * (config_small.spatial_scale_y / config_small.phase_wrap)
    
    x_large = test_phi_x * (config_large.spatial_scale_x / config_large.phase_wrap)
    y_large = test_phi_y * (config_large.spatial_scale_y / config_large.phase_wrap)
    
    engine_small.reset(x_small, y_small)
    engine_large.reset(x_large, y_large)
    
    state_small = engine_small.get_state()
    state_large = engine_large.get_state()
    
    # 위상은 스케일과 무관하게 일치해야 함 (정규화 후)
    phi_x_small_norm = normalize_phase(state_small.phi_x, config_small.phase_wrap)
    phi_y_small_norm = normalize_phase(state_small.phi_y, config_small.phase_wrap)
    
    phi_x_large_norm = normalize_phase(state_large.phi_x, config_large.phase_wrap)
    phi_y_large_norm = normalize_phase(state_large.phi_y, config_large.phase_wrap)
    
    assert abs(phi_x_small_norm - phi_x_large_norm) < 1e-6
    assert abs(phi_y_small_norm - phi_y_large_norm) < 1e-6


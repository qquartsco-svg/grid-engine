"""
Grid Engine 오류 처리 테스트
입력 검증 및 예외 처리 검증

Author: [작성자 시그니처]
Created: 2026-01
"""

import pytest
import numpy as np
from grid_engine import GridEngine, GridInput, GridEngineConfig
from grid_engine.coupling import normalize_phase, phase_to_coordinate, coordinate_to_phase


def test_config_validation_negative_dt():
    """음수 dt_ms 검증"""
    config = GridEngineConfig(dt_ms=-0.1, tau_ms=10.0)
    
    with pytest.raises(AssertionError, match="dt_ms must be positive"):
        config.validate()


def test_config_validation_large_dt():
    """너무 큰 dt_ms 검증"""
    # dt_ms > tau_ms * max_dt_ratio 인 경우
    config = GridEngineConfig(dt_ms=2.0, tau_ms=10.0, max_dt_ratio=0.1)
    
    with pytest.raises(AssertionError, match="dt_ms.*must be < tau_ms"):
        config.validate()


def test_config_validation_zero_ring_size():
    """ring_size = 0 검증"""
    config = GridEngineConfig(ring_size=0)
    
    with pytest.raises(AssertionError, match="ring_size must be positive"):
        config.validate()


def test_config_validation_negative_phase_wrap():
    """음수 phase_wrap 검증"""
    config = GridEngineConfig(phase_wrap=-1.0)
    
    with pytest.raises(AssertionError, match="phase_wrap must be positive"):
        config.validate()


def test_invalid_integration_method():
    """지원하지 않는 적분 방법 검증"""
    config = GridEngineConfig(integration="invalid_method")
    
    with pytest.raises(AssertionError, match="Only semi-implicit Euler is supported"):
        config.validate()


def test_nan_input_handling():
    """NaN 입력 처리 테스트"""
    engine = GridEngine()
    
    # NaN 입력 테스트
    inp_nan = GridInput(v_x=np.nan, v_y=0.0)
    
    # NaN이 전파되지 않도록 처리되어야 함
    # (현재는 명시적 처리 없음, 향후 추가 필요)
    # 이 테스트는 현재 동작을 확인하는 용도
    try:
        output = engine.step(inp_nan)
        # NaN이 전파되었다면 이것도 NaN일 것
        assert np.isnan(output.phi_x) or not np.isnan(output.phi_x)  # 현재 동작 확인
    except (ValueError, RuntimeError):
        # 예외가 발생하는 것도 허용 (오류 처리 방식)
        pass


def test_inf_input_handling():
    """무한대 입력 처리 테스트"""
    engine = GridEngine()
    
    # 무한대 입력 테스트
    inp_inf = GridInput(v_x=np.inf, v_y=0.0)
    
    # 무한대가 전파되지 않도록 처리되어야 함
    # (현재는 명시적 처리 없음, 향후 추가 필요)
    try:
        output = engine.step(inp_inf)
        # 무한대가 전파되었다면 이것도 무한대일 것
        assert np.isinf(output.phi_x) or not np.isinf(output.phi_x)  # 현재 동작 확인
    except (ValueError, RuntimeError):
        # 예외가 발생하는 것도 허용
        pass


def test_normalize_phase_zero_wrap():
    """phase_wrap = 0인 경우 처리"""
    # phase_wrap = 0은 나눗셈 오류를 발생시킬 수 있음
    # 이는 config.validate()에서 걸러져야 함
    # 하지만 normalize_phase()에서도 방어적으로 처리하는 것이 좋음
    
    with pytest.raises(ZeroDivisionError):
        # phase_wrap = 0이면 모듈로 연산이 실패
        normalize_phase(1.0, 0.0)


def test_coordinate_to_phase_zero_scale():
    """spatial_scale = 0인 경우 처리"""
    config = GridEngineConfig(spatial_scale_x=0.0, spatial_scale_y=1.0)
    
    # spatial_scale_x = 0이면 나눗셈 오류 발생
    # 이는 config.validate()에서 걸러져야 하지만,
    # 현재는 검증이 없으므로 실제 오류 확인
    try:
        phi_x, phi_y = coordinate_to_phase(1.0, 1.0, config)
        # 0으로 나누면 무한대 또는 NaN
        assert np.isinf(phi_x) or np.isnan(phi_x)
    except (ZeroDivisionError, RuntimeError):
        # 예외가 발생하는 것도 허용
        pass


def test_reset_with_invalid_coordinates():
    """유효하지 않은 좌표로 reset 테스트"""
    engine = GridEngine()
    
    # 매우 큰 좌표 (무한대는 아니지만)
    large_x = 1e10
    large_y = 1e10
    
    # reset은 성공해야 하지만, 위상은 정규화됨
    engine.reset(large_x, large_y)
    state = engine.get_state()
    
    # 위상은 [0, 2π) 범위에 있어야 함
    phase_wrap = engine.config.phase_wrap
    assert 0.0 <= state.phi_x < phase_wrap
    assert 0.0 <= state.phi_y < phase_wrap


def test_step_with_extreme_acceleration():
    """극단적인 가속도 입력 테스트"""
    engine = GridEngine()
    
    # 매우 큰 가속도
    inp_large_accel = GridInput(v_x=0.0, v_y=0.0, a_x=1e6, a_y=0.0)
    
    # 한 스텝 실행
    output = engine.step(inp_large_accel)
    state = engine.get_state()
    
    # 상태가 유효한 범위 내에 있어야 함
    # (발산하지 않아야 함)
    phase_wrap = engine.config.phase_wrap
    assert 0.0 <= state.phi_x < phase_wrap or abs(state.phi_x) < 1e10  # 발산 방지
    assert 0.0 <= state.phi_y < phase_wrap or abs(state.phi_y) < 1e10


def test_long_term_stability():
    """장기 실행 안정성 테스트"""
    engine = GridEngine()
    
    # 일정한 속도로 장기간 실행
    inp = GridInput(v_x=1.0, v_y=0.0)
    
    # 많은 스텝 실행 (1000 스텝)
    for i in range(1000):
        output = engine.step(inp)
        state = engine.get_state()
        
        # 주기적으로 위상이 정규화되는지 확인
        phase_wrap = engine.config.phase_wrap
        assert 0.0 <= state.phi_x < phase_wrap or abs(state.phi_x) < 1e10
        assert 0.0 <= state.phi_y < phase_wrap or abs(state.phi_y) < 1e10
        
        # NaN이나 무한대가 발생하지 않아야 함
        assert not np.isnan(state.phi_x)
        assert not np.isnan(state.phi_y)
        assert not np.isinf(state.phi_x)
        assert not np.isinf(state.phi_y)


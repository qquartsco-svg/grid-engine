"""
Grid Engine Fail-Safe 테스트
"""

import pytest
from grid_engine import GridEngine, GridInput, GridEngineConfig


def test_fail_safe_large_velocity():
    """큰 속도 입력에도 안정성 유지"""
    engine = GridEngine()
    
    # 매우 큰 속도 입력
    inp = GridInput(v_x=100.0, v_y=100.0)
    
    # 여러 스텝 실행
    for _ in range(10):
        output = engine.step(inp)
        
        # 상태가 유효한 범위 내에 있는지 확인
        assert abs(output.x) < 1e6  # 무한대로 발산하지 않음
        assert abs(output.y) < 1e6
        assert 0.0 <= output.phi_x < 2 * 3.141592653589793
        assert 0.0 <= output.phi_y < 2 * 3.141592653589793


def test_fail_safe_invalid_config():
    """잘못된 설정 검증"""
    # dt가 너무 큰 경우
    config = GridEngineConfig(
        dt_ms=10.0,  # tau보다 큼
        tau_ms=5.0
    )
    
    with pytest.raises(AssertionError):
        config.validate()


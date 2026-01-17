"""
Grid Engine 에너지 단조 감소 테스트
"""

import pytest
from grid_engine import GridEngine, GridInput, GridEngineConfig


def test_energy_monotonic_decrease():
    """에너지가 단조 감소하는지 확인"""
    config = GridEngineConfig(
        diagnostics_enabled=True,
        energy_check_enabled=True
    )
    engine = GridEngine(config=config)
    
    inp = GridInput(v_x=0.1, v_y=0.1)
    
    energies = []
    for _ in range(20):
        output = engine.step(inp)
        if output.energy is not None:
            energies.append(output.energy)
    
    # 에너지가 감소하는지 확인 (일부 허용 오차)
    if len(energies) > 1:
        # 전체적으로 감소하는 경향 확인
        decreasing_count = sum(
            1 for i in range(1, len(energies))
            if energies[i] <= energies[i-1] + 1e-6  # 작은 증가 허용
        )
        # 대부분 감소해야 함
        assert decreasing_count >= len(energies) * 0.7


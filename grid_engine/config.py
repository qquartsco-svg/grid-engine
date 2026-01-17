"""
Grid Engine Configuration
모든 상수/튜닝 파라미터 (하드코딩 금지)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GridEngineConfig:
    """
    Grid Engine 설정
    
    모든 튜닝 가능한 파라미터는 여기에 집중
    하드코딩 금지 원칙
    """
    # 시간 관련
    dt_ms: float = 0.1  # 시간 간격 [ms]
    tau_ms: float = 10.0  # 시간 상수 [ms]
    
    # 수치 적분 방법
    integration: str = "semi_implicit"  # 고정: semi-implicit Euler
    
    # Ring Engine 설정 (X, Y 각각)
    ring_cfg_x: str = "case2"  # X 방향 Ring 설정
    ring_cfg_y: str = "case2"  # Y 방향 Ring 설정
    ring_size: int = 15  # Ring 크기 (뉴런 수)
    
    # 위상 관련
    phase_wrap: float = 2.0 * 3.141592653589793  # 2π [rad]
    
    # 공간 스케일 (도메인 길이)
    # spatial_scale_x: 위상 2π가 대응하는 실제 공간 길이 [m]
    # x = phi_x * (spatial_scale_x / 2π)
    # 예: spatial_scale_x = 10.0 → 2π rad = 10.0 m
    spatial_scale_x: float = 1.0  # X 방향 도메인 길이 [m] (2π rad에 대응)
    spatial_scale_y: float = 1.0  # Y 방향 도메인 길이 [m] (2π rad에 대응)
    
    # 진단 모드
    diagnostics_enabled: bool = False  # 에너지/안정성 진단 활성화
    
    # 안정성 검증
    energy_check_enabled: bool = True  # 에너지 감소 검증
    stability_threshold: float = 0.1  # 안정성 임계값
    
    # 수치 안정성
    max_dt_ratio: float = 0.1  # dt < tau * max_dt_ratio (안정 조건)
    
    def validate(self) -> None:
        """
        설정 유효성 검증
        
        모든 파라미터가 유효한 범위 내에 있는지 확인합니다.
        잘못된 설정은 수치 불안정성이나 물리적으로 무의미한 결과를
        초래할 수 있으므로 사전에 검증합니다.
        
        검증 항목:
            - dt_ms > 0: 시간 간격은 양수여야 함
            - tau_ms > 0: 시간 상수는 양수여야 함
            - dt_ms < tau_ms * max_dt_ratio: 수치 안정성 조건
            - integration == "semi_implicit": 지원하는 적분 방법만 허용
            - ring_size > 0: Ring 크기는 양수여야 함
            - phase_wrap > 0: 위상 범위는 양수여야 함
            - spatial_scale_x > 0: 공간 스케일은 양수여야 함
            - spatial_scale_y > 0: 공간 스케일은 양수여야 함
        
        Raises:
            AssertionError: 설정이 유효하지 않은 경우
        
        Author: GNJz
        Created: 2026-01-20
        Made in GNJz
        """
        assert self.dt_ms > 0, "dt_ms must be positive"
        assert self.tau_ms > 0, "tau_ms must be positive"
        assert self.dt_ms < self.tau_ms * self.max_dt_ratio, \
            f"dt_ms ({self.dt_ms}) must be < tau_ms * max_dt_ratio ({self.tau_ms * self.max_dt_ratio})"
        assert self.integration == "semi_implicit", \
            "Only semi-implicit Euler is supported"
        assert self.ring_size > 0, "ring_size must be positive"
        assert self.phase_wrap > 0, "phase_wrap must be positive"
        assert self.spatial_scale_x > 0, "spatial_scale_x must be positive"
        assert self.spatial_scale_y > 0, "spatial_scale_y must be positive"


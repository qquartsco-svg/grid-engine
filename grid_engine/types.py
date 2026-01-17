"""
Grid Engine Types
모든 데이터 클래스 정의 (State/Input/Output/Diagnostics)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class GridState:
    """
    Grid Engine 내부 상태
    
    내부 상태: 위상 벡터 (φx, φy)
    외부 표현: 공간 좌표 (x, y)
    """
    # 위상 (내부 상태)
    phi_x: float  # X 방향 위상 [0, 2π)
    phi_y: float  # Y 방향 위상 [0, 2π)
    
    # 좌표 (외부 표현)
    x: float  # X 좌표
    y: float  # Y 좌표
    
    # 속도
    v_x: float  # X 방향 속도
    v_y: float  # Y 방향 속도
    
    # 가속도
    a_x: float  # X 방향 가속도
    a_y: float  # Y 방향 가속도
    
    # 시간
    t_ms: float  # 현재 시간 [ms]
    
    def __post_init__(self):
        """
        위상 범위 검증
        
        주의: config.phase_wrap을 사용해야 하지만,
        dataclass 초기화 시점에는 config가 없으므로
        기본값 2π를 사용합니다.
        실제 정규화는 coupling.normalize_phase()에서 수행됩니다.
        """
        # 위상 주기적 경계 조건 (기본값 2π 사용)
        phase_wrap_default = 2.0 * 3.141592653589793
        self.phi_x = self.phi_x % phase_wrap_default
        self.phi_y = self.phi_y % phase_wrap_default


@dataclass
class GridInput:
    """
    Grid Engine 입력
    
    속도/가속도 벡터 입력
    """
    v_x: float  # X 방향 속도
    v_y: float  # Y 방향 속도
    
    # 가속도 (선택적)
    a_x: Optional[float] = None  # X 방향 가속도
    a_y: Optional[float] = None  # Y 방향 가속도
    
    # 외부 편향 (선택적)
    external_bias: Optional[Tuple[float, float]] = None  # (bias_x, bias_y)


@dataclass
class GridOutput:
    """
    Grid Engine 출력
    
    외부 표현: 좌표 (x, y)
    내부 상태: 위상 (φx, φy)
    """
    # 좌표 (외부 표현)
    x: float  # X 좌표
    y: float  # Y 좌표
    
    # 위상 (내부 상태)
    phi_x: float  # X 방향 위상 [0, 2π)
    phi_y: float  # Y 방향 위상 [0, 2π)
    
    # 안정성 점수 (선택적)
    stability_score: Optional[float] = None  # [0, 1]
    
    # 에너지 (선택적)
    energy: Optional[float] = None


@dataclass
class GridDiagnostics:
    """
    Grid Engine 진단 정보
    
    에너지, 안정성, 오차 등 진단용 데이터
    """
    # 에너지
    energy: float  # 현재 에너지
    energy_change: float  # 에너지 변화 (dE/dt)
    energy_decreasing: bool  # 에너지 감소 여부
    
    # 안정성
    stability_score: float  # 안정성 점수 [0, 1]
    
    # 위상 안정성
    phi_x_stability: float  # X 위상 안정성
    phi_y_stability: float  # Y 위상 안정성
    
    # 수치 안정성
    dt_ratio: float  # dt / tau 비율
    is_stable: bool  # 수치 안정성 여부


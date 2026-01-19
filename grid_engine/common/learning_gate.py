"""
Learning Gate Module
Place/Context 학습을 제어하는 Gate 메커니즘

핵심 개념:
- "언제 학습해야 하는지"에 대한 명시적 제한
- 기본 OFF, 조건 만족 시에만 ON
- 일시적 노이즈를 '기억'으로 저장하는 것을 방지

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.1-alpha (Learning Gate extension)
License: MIT License
"""

from typing import Optional, Dict, Any
import numpy as np
from dataclasses import dataclass


@dataclass
class LearningGateConfig:
    """
    Learning Gate 설정
    
    학습 조건을 명시적으로 제한합니다.
    """
    # 속도 임계값
    velocity_threshold: float = 0.01  # [m/s] 또는 [deg/s]
    
    # 가속도 임계값
    acceleration_threshold: float = 0.001  # [m/s²] 또는 [deg/s²]
    
    # 최근 N 스텝 분산 임계값
    variance_window: int = 10  # 최근 10 스텝
    variance_threshold: float = 0.0001  # 분산 임계값
    
    # 동일 place 재방문 횟수
    min_visit_count: int = 3  # 최소 3회 방문해야 학습
    
    # 기본 상태 (기본 OFF)
    default_enabled: bool = False  # 기본적으로 학습 비활성화
    
    # Replay phase에서만 업데이트
    replay_only: bool = True  # Replay phase에서만 업데이트


class LearningGate:
    """
    Place/Context 학습을 제어하는 Gate
    
    생물학적 근거:
    - Place Cell은 항상 학습하지 않는다
    - Replay는 노이즈를 평균낸 뒤 일어난다
    - CA1은 상태가 안정될 때만 LTP가 일어난다
    """
    
    def __init__(self, config: Optional[LearningGateConfig] = None):
        """
        Learning Gate 초기화
        
        Args:
            config: Learning Gate 설정 (None이면 기본값)
        """
        self.config = config or LearningGateConfig()
        
        # 상태 추적
        self.recent_states: list = []  # 최근 N 스텝 상태 기록
        self.recent_velocities: list = []  # 최근 N 스텝 속도 기록
        self.recent_accelerations: list = []  # 최근 N 스텝 가속도 기록
    
    def should_learn(
        self,
        current_state: np.ndarray,
        current_velocity: Optional[np.ndarray] = None,
        current_acceleration: Optional[np.ndarray] = None,
        place_visit_count: int = 0,
        is_replay_phase: bool = False
    ) -> bool:
        """
        학습을 수행해야 하는지 판단
        
        조건 (하나라도 만족해야 학습):
        1. 속도 < threshold
        2. 가속도 < threshold
        3. 최근 N step 분산 < threshold
        4. 동일 place 재방문 횟수 ≥ K
        5. replay phase에서만 update (replay_only=True인 경우)
        
        Args:
            current_state: 현재 상태 [x, y, z, theta_a, theta_b]
            current_velocity: 현재 속도 (None이면 계산)
            current_acceleration: 현재 가속도 (None이면 계산)
            place_visit_count: 동일 place 방문 횟수
            is_replay_phase: Replay phase 여부
        
        Returns:
            학습 수행 여부
        """
        # 기본 상태가 OFF이면 항상 False
        if not self.config.default_enabled:
            # Replay phase에서만 학습 (replay_only=True인 경우)
            if self.config.replay_only:
                return is_replay_phase
            
            # Replay phase가 아니면 추가 조건 확인
            if not is_replay_phase:
                return False
        
        # 상태 기록 업데이트
        self.recent_states.append(current_state.copy())
        if len(self.recent_states) > self.config.variance_window:
            self.recent_states.pop(0)
        
        # 속도 기록 업데이트
        if current_velocity is not None:
            self.recent_velocities.append(current_velocity.copy())
            if len(self.recent_velocities) > self.config.variance_window:
                self.recent_velocities.pop(0)
        
        # 가속도 기록 업데이트
        if current_acceleration is not None:
            self.recent_accelerations.append(current_acceleration.copy())
            if len(self.recent_accelerations) > self.config.variance_window:
                self.recent_accelerations.pop(0)
        
        # 조건 1: 속도 임계값 확인
        if current_velocity is not None:
            velocity_norm = np.linalg.norm(current_velocity)
            if velocity_norm > self.config.velocity_threshold:
                return False  # 속도가 너무 빠르면 학습 안 함
        
        # 조건 2: 가속도 임계값 확인
        if current_acceleration is not None:
            acceleration_norm = np.linalg.norm(current_acceleration)
            if acceleration_norm > self.config.acceleration_threshold:
                return False  # 가속도가 너무 크면 학습 안 함
        
        # 조건 3: 최근 N 스텝 분산 확인
        if len(self.recent_states) >= self.config.variance_window:
            states_array = np.array(self.recent_states)
            variance = np.var(states_array, axis=0)
            variance_norm = np.linalg.norm(variance)
            if variance_norm > self.config.variance_threshold:
                return False  # 분산이 너무 크면 학습 안 함
        
        # 조건 4: 동일 place 재방문 횟수 확인
        if place_visit_count < self.config.min_visit_count:
            return False  # 충분히 방문하지 않았으면 학습 안 함
        
        # 모든 조건 만족 → 학습 가능
        return True
    
    def reset(self):
        """상태 초기화"""
        self.recent_states = []
        self.recent_velocities = []
        self.recent_accelerations = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Learning Gate 통계 정보"""
        return {
            "recent_states_count": len(self.recent_states),
            "recent_velocities_count": len(self.recent_velocities),
            "recent_accelerations_count": len(self.recent_accelerations),
            "config": {
                "velocity_threshold": self.config.velocity_threshold,
                "acceleration_threshold": self.config.acceleration_threshold,
                "variance_window": self.config.variance_window,
                "variance_threshold": self.config.variance_threshold,
                "min_visit_count": self.config.min_visit_count,
                "default_enabled": self.config.default_enabled,
                "replay_only": self.config.replay_only
            }
        }


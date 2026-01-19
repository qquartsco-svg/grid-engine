"""
Cerebellum Engine
소뇌(Cerebellum) 엔진 - 기억을 즉각 행동으로 변환하는 계층

핵심 개념:
- 해마의 기억을 즉각 행동으로 변환
- Predictive Feedforward: 다음 순간의 오차 예측
- Trial-to-Trial 보정: 반복 궤적의 미세 편차 제거
- Variance 감소: 미세한 떨림 필터링

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.5.0-alpha (Cerebellum Engine)
License: MIT License
"""

from typing import Dict, Any, Optional, List
import numpy as np
from collections import deque
from dataclasses import dataclass, field


@dataclass
class CerebellumConfig:
    """소뇌 설정"""
    # Predictive Feedforward
    feedforward_gain: float = 0.5  # 피드포워드 gain
    prediction_horizon: float = 0.01  # 예측 시간 (초)
    
    # Trial-to-Trial 보정
    trial_gain: float = 0.3  # Trial 보정 gain
    
    # Variance 감소
    variance_gain: float = 0.2  # Variance 감소 gain
    low_pass_cutoff: float = 10.0  # 저주파 필터 차단 주파수 (Hz)
    variance_window: int = 5  # 분산 계산 윈도우 크기
    
    # 기억 기반 적응
    memory_gain: float = 0.4  # 기억 기반 보정 gain
    
    # 통합
    correction_weight: float = 1.0  # 전체 보정 가중치


class CerebellumEngine:
    """
    소뇌 엔진
    
    해마의 기억을 즉각 행동으로 변환하는 계층
    
    역할:
    1. Predictive Feedforward: 다음 순간의 오차 예측
    2. Trial-to-Trial 보정: 반복 궤적의 미세 편차 제거
    3. Variance 감소: 미세한 떨림 필터링
    4. 기억 기반 적응: 해마의 기억을 즉각 행동으로 변환
    """
    
    def __init__(
        self,
        memory_dim: int = 5,
        config: Optional[CerebellumConfig] = None,
        memory: Optional[Any] = None  # UniversalMemory 인스턴스
    ):
        """
        소뇌 엔진 초기화
        
        Args:
            memory_dim: 메모리 차원 (기본값: 5D)
            config: 소뇌 설정 (None이면 기본값)
            memory: 해마 메모리 인스턴스 (None이면 나중에 설정)
        """
        self.memory_dim = memory_dim
        self.config = config or CerebellumConfig()
        self.memory = memory
        
        # 상태 기록 (Variance 감소용)
        self.error_history: deque = deque(maxlen=self.config.variance_window)
        self.state_history: deque = deque(maxlen=self.config.variance_window)
        
        # 이전 상태 (예측용)
        self.prev_state: Optional[np.ndarray] = None
        self.prev_velocity: Optional[np.ndarray] = None
        self.prev_time: float = 0.0
        
        # 저주파 필터 상태 (Variance 감소용)
        self.filtered_error: Optional[np.ndarray] = None
    
    def set_memory(self, memory: Any) -> None:
        """
        해마 메모리 설정
        
        Args:
            memory: UniversalMemory 인스턴스
        """
        self.memory = memory
    
    def compute_correction(
        self,
        current_state: np.ndarray,
        target_state: np.ndarray,
        velocity: Optional[np.ndarray] = None,
        acceleration: Optional[np.ndarray] = None,
        context: Optional[Dict[str, Any]] = None,
        dt: float = 0.001  # 시간 간격 (초, 기본값: 1ms)
    ) -> np.ndarray:
        """
        소뇌 보정값 계산
        
        해마의 기억을 활용하여 즉각 보정값을 계산합니다.
        
        Args:
            current_state: 현재 상태 [x, y, z, theta_a, theta_b]
            target_state: 목표 상태 [x, y, z, theta_a, theta_b]
            velocity: 현재 속도 (None이면 계산)
            acceleration: 현재 가속도 (None이면 계산)
            context: 맥락 정보 (해마 메모리 검색용)
            dt: 시간 간격 (초)
        
        Returns:
            cerebellum_correction: 소뇌 보정값 [x, y, z, theta_a, theta_b]
        """
        # 현재 오차 계산
        current_error = target_state - current_state
        
        # 상태 기록 업데이트
        self.error_history.append(current_error.copy())
        self.state_history.append(current_state.copy())
        
        # 속도/가속도 계산 (제공되지 않은 경우)
        if velocity is None:
            velocity = self._estimate_velocity(current_state, dt)
        if acceleration is None:
            acceleration = self._estimate_acceleration(velocity, dt)
        
        # 1. 해마에서 기억 검색 (기억 기반 적응)
        memory_bias = self._get_memory_bias(current_state, context)
        
        # 2. Predictive Feedforward (다음 순간의 오차 예측)
        predicted_error = self._predict_error(
            current_error,
            velocity,
            acceleration,
            dt
        )
        feedforward_correction = -predicted_error * self.config.feedforward_gain
        
        # 3. Trial-to-Trial 보정 (반복 궤적의 미세 편차 제거)
        trial_correction = self._compute_trial_correction(
            current_error,
            memory_bias
        )
        
        # 4. Variance 감소 (미세한 떨림 필터링)
        variance_correction = self._reduce_variance(current_error)
        
        # 5. 기억 기반 적응 (해마의 기억을 즉각 행동으로 변환)
        memory_correction = -memory_bias * self.config.memory_gain
        
        # 6. 통합 보정
        total_correction = (
            feedforward_correction +
            trial_correction +
            variance_correction +
            memory_correction
        ) * self.config.correction_weight
        
        # 이전 상태 업데이트
        self.prev_state = current_state.copy()
        self.prev_velocity = velocity.copy()
        
        return total_correction
    
    def _get_memory_bias(
        self,
        current_state: np.ndarray,
        context: Optional[Dict[str, Any]]
    ) -> np.ndarray:
        """
        해마 메모리에서 기억된 bias 검색
        
        Args:
            current_state: 현재 상태
            context: 맥락 정보
        
        Returns:
            memory_bias: 기억된 bias (없으면 0 벡터)
        """
        if self.memory is None:
            return np.zeros(self.memory_dim)
        
        try:
            # 해마 메모리에서 기억 검색
            memories = self.memory.retrieve(current_state, context or {})
            
            if memories:
                # 첫 번째 기억의 bias 사용
                memory_bias = memories[0].get('bias', np.zeros(self.memory_dim))
                return memory_bias
            else:
                return np.zeros(self.memory_dim)
        except Exception:
            # 오류 발생 시 0 벡터 반환
            return np.zeros(self.memory_dim)
    
    def _predict_error(
        self,
        current_error: np.ndarray,
        velocity: np.ndarray,
        acceleration: np.ndarray,
        dt: float
    ) -> np.ndarray:
        """
        다음 순간의 오차 예측 (Predictive Feedforward)
        
        수식: predicted_error = current_error + velocity * dt + 0.5 * acceleration * dt²
        
        Args:
            current_error: 현재 오차
            velocity: 현재 속도
            acceleration: 현재 가속도
            dt: 시간 간격
        
        Returns:
            predicted_error: 예측된 오차
        """
        # 예측 시간
        prediction_dt = self.config.prediction_horizon
        
        # 예측 오차 계산
        predicted_error = (
            current_error +
            velocity * prediction_dt +
            0.5 * acceleration * prediction_dt ** 2
        )
        
        return predicted_error
    
    def _compute_trial_correction(
        self,
        current_error: np.ndarray,
        memory_bias: np.ndarray
    ) -> np.ndarray:
        """
        Trial-to-Trial 보정 계산
        
        반복되는 궤적에서의 미세한 편차를 제거합니다.
        
        수식: trial_error = current_error - memory_bias
              trial_correction = -trial_error * trial_gain
        
        Args:
            current_error: 현재 오차
            memory_bias: 기억된 bias
        
        Returns:
            trial_correction: Trial 보정값
        """
        # Trial 오차 계산 (기억된 bias와 현재 오차의 차이)
        trial_error = current_error - memory_bias
        
        # Trial 보정
        trial_correction = -trial_error * self.config.trial_gain
        
        return trial_correction
    
    def _reduce_variance(
        self,
        current_error: np.ndarray
    ) -> np.ndarray:
        """
        Variance 감소 (미세한 떨림 필터링)
        
        저주파 필터를 사용하여 고주파 노이즈를 제거합니다.
        
        Args:
            current_error: 현재 오차
        
        Returns:
            variance_correction: Variance 감소 보정값
        """
        # 저주파 필터 적용 (단순 이동 평균)
        if len(self.error_history) < self.config.variance_window:
            # 윈도우가 채워지지 않았으면 현재 오차 사용
            filtered_error = current_error.copy()
        else:
            # 이동 평균 필터
            error_array = np.array(list(self.error_history))
            filtered_error = np.mean(error_array, axis=0)
        
        # 필터링된 오차 저장
        self.filtered_error = filtered_error
        
        # Variance 보정 (고주파 노이즈 제거)
        high_freq_noise = current_error - filtered_error
        variance_correction = -high_freq_noise * self.config.variance_gain
        
        return variance_correction
    
    def _estimate_velocity(
        self,
        current_state: np.ndarray,
        dt: float
    ) -> np.ndarray:
        """
        속도 추정 (이전 상태 기반)
        
        Args:
            current_state: 현재 상태
            dt: 시간 간격
        
        Returns:
            velocity: 추정된 속도
        """
        if self.prev_state is None or dt <= 0:
            return np.zeros(self.memory_dim)
        
        velocity = (current_state - self.prev_state) / dt
        return velocity
    
    def _estimate_acceleration(
        self,
        velocity: np.ndarray,
        dt: float
    ) -> np.ndarray:
        """
        가속도 추정 (이전 속도 기반)
        
        Args:
            velocity: 현재 속도
            dt: 시간 간격
        
        Returns:
            acceleration: 추정된 가속도
        """
        if self.prev_velocity is None or dt <= 0:
            return np.zeros(self.memory_dim)
        
        acceleration = (velocity - self.prev_velocity) / dt
        return acceleration
    
    def reset(self) -> None:
        """소뇌 엔진 리셋"""
        self.error_history.clear()
        self.state_history.clear()
        self.prev_state = None
        self.prev_velocity = None
        self.filtered_error = None


# 편의 함수: 소뇌 엔진 생성
def create_cerebellum_engine(
    memory_dim: int = 5,
    config: Optional[CerebellumConfig] = None,
    memory: Optional[Any] = None
) -> CerebellumEngine:
    """
    소뇌 엔진 생성 (편의 함수)
    
    Args:
        memory_dim: 메모리 차원
        config: 소뇌 설정
        memory: 해마 메모리 인스턴스
    
    Returns:
        CerebellumEngine 인스턴스
    """
    return CerebellumEngine(
        memory_dim=memory_dim,
        config=config,
        memory=memory
    )


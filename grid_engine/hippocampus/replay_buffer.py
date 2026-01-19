"""
Replay Buffer Module
Online phase에서 trajectory/error/state를 기록하는 버퍼

핵심 개념:
- Online phase: 기록만 (bias 업데이트 금지)
- Replay phase: 기록된 데이터를 재생하여 학습

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.1-alpha (Replay Buffer extension)
License: MIT License
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import numpy as np
from collections import deque


@dataclass
class TrajectoryPoint:
    """
    궤적 포인트 데이터
    
    Online phase에서 기록되는 단일 시점의 데이터
    """
    timestamp: float  # 시간 (ms)
    phase_vector: np.ndarray  # 위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b]
    current_state: np.ndarray  # 현재 상태 [x, y, z, theta_a, theta_b]
    target_state: np.ndarray  # 목표 상태 [x, y, z, theta_a, theta_b]
    error: np.ndarray  # 오차 (current - target)
    velocity: np.ndarray  # 속도 [v_x, v_y, v_z, v_a, v_b]
    acceleration: np.ndarray  # 가속도 [a_x, a_y, a_z, alpha_a, alpha_b]
    place_id: int  # Place ID
    context_id: Optional[int] = None  # Context ID (None이면 Context 없음)
    
    def is_stable(
        self,
        velocity_threshold: float = 0.01,
        acceleration_threshold: float = 0.001,
        variance_threshold: float = 0.0001
    ) -> bool:
        """
        안정적인 구간인지 판단
        
        조건:
        - 속도 < threshold
        - 가속도 < threshold
        - 오차 분산 < threshold (단일 포인트이므로 항상 True)
        
        Args:
            velocity_threshold: 속도 임계값
            acceleration_threshold: 가속도 임계값
            variance_threshold: 분산 임계값 (사용 안 함, 단일 포인트)
        
        Returns:
            안정적인 구간 여부
        """
        velocity_norm = np.linalg.norm(self.velocity)
        acceleration_norm = np.linalg.norm(self.acceleration)
        
        return (velocity_norm < velocity_threshold and
                acceleration_norm < acceleration_threshold)


class ReplayBuffer:
    """
    Replay Buffer
    
    Online phase에서 trajectory/error/state를 기록하고,
    Replay phase에서 안정적인 구간만 재생합니다.
    """
    
    def __init__(
        self,
        max_size: int = 10000,  # 최대 버퍼 크기
        stable_window: int = 10  # 안정성 판단 윈도우 (최근 N 포인트)
    ):
        """
        Replay Buffer 초기화
        
        Args:
            max_size: 최대 버퍼 크기
            stable_window: 안정성 판단 윈도우 크기
        """
        self.max_size = max_size
        self.stable_window = stable_window
        
        # 버퍼 (deque 사용하여 자동 오버플로우 처리)
        self.buffer: deque = deque(maxlen=max_size)
        
        # 통계
        self.total_points: int = 0
        self.stable_points: int = 0
    
    def add_point(
        self,
        timestamp: float,
        phase_vector: np.ndarray,
        current_state: np.ndarray,
        target_state: np.ndarray,
        error: np.ndarray,
        velocity: np.ndarray,
        acceleration: np.ndarray,
        place_id: int,
        context_id: Optional[int] = None
    ) -> None:
        """
        궤적 포인트 추가 (Online phase)
        
        Args:
            timestamp: 시간 (ms)
            phase_vector: 위상 벡터
            current_state: 현재 상태
            target_state: 목표 상태
            error: 오차
            velocity: 속도
            acceleration: 가속도
            place_id: Place ID
            context_id: Context ID (None이면 Context 없음)
        """
        point = TrajectoryPoint(
            timestamp=timestamp,
            phase_vector=phase_vector.copy(),
            current_state=current_state.copy(),
            target_state=target_state.copy(),
            error=error.copy(),
            velocity=velocity.copy(),
            acceleration=acceleration.copy(),
            place_id=place_id,
            context_id=context_id
        )
        
        self.buffer.append(point)
        self.total_points += 1
        
        # 안정적인 포인트인지 확인
        if point.is_stable():
            self.stable_points += 1
    
    def get_stable_segments(
        self,
        velocity_threshold: float = 0.01,
        acceleration_threshold: float = 0.001,
        min_segment_length: int = 5
    ) -> List[List[TrajectoryPoint]]:
        """
        안정적인 구간만 추출 (Replay phase용)
        
        조건:
        - 저속·저가속·저분산 구간만
        - 최소 구간 길이 이상
        
        Args:
            velocity_threshold: 속도 임계값
            acceleration_threshold: 가속도 임계값
            min_segment_length: 최소 구간 길이
        
        Returns:
            안정적인 구간 리스트 (각 구간은 TrajectoryPoint 리스트)
        """
        if len(self.buffer) < min_segment_length:
            return []
        
        stable_segments = []
        current_segment = []
        
        for point in self.buffer:
            if point.is_stable(velocity_threshold, acceleration_threshold):
                current_segment.append(point)
            else:
                # 안정적인 구간이 끝남
                if len(current_segment) >= min_segment_length:
                    stable_segments.append(current_segment)
                current_segment = []
        
        # 마지막 구간 처리
        if len(current_segment) >= min_segment_length:
            stable_segments.append(current_segment)
        
        return stable_segments
    
    def get_place_bias_data(
        self,
        place_id: int,
        context_id: Optional[int] = None
    ) -> List[TrajectoryPoint]:
        """
        특정 Place (및 Context)의 데이터만 추출
        
        Args:
            place_id: Place ID
            context_id: Context ID (None이면 Context 무시)
        
        Returns:
            해당 Place의 TrajectoryPoint 리스트
        """
        if context_id is None:
            # Context 무시
            return [p for p in self.buffer if p.place_id == place_id]
        else:
            # Place + Context 조합
            return [p for p in self.buffer 
                   if p.place_id == place_id and p.context_id == context_id]
    
    def clear(self):
        """버퍼 초기화"""
        self.buffer.clear()
        self.total_points = 0
        self.stable_points = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Replay Buffer 통계 정보"""
        return {
            "buffer_size": len(self.buffer),
            "total_points": self.total_points,
            "stable_points": self.stable_points,
            "stable_ratio": self.stable_points / self.total_points if self.total_points > 0 else 0.0,
            "max_size": self.max_size
        }


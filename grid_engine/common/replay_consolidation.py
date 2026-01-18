"""
Replay/Consolidation Module
휴지기에 기억을 재검토하고 강화하는 Replay/Consolidation 구현

핵심 개념:
- "가만히 있을 때 더 똑똑해짐"
- 일시적 노이즈 필터링
- 진짜 편향만 장기 기억으로 고정

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (Replay/Consolidation extension)
License: MIT License
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from collections import deque


@dataclass
class PlaceMemoryWithHistory:
    """
    Place Memory with Bias History (Replay/Consolidation용)
    
    최근 N회차의 bias 이력을 저장하여 노이즈 필터링에 사용합니다.
    """
    place_id: int
    bias_estimate: np.ndarray = field(default_factory=lambda: np.zeros(5))  # 장기 기억 (Consolidated)
    bias_history: deque = field(default_factory=lambda: deque(maxlen=10))  # 최근 10회차 bias 이력
    visit_count: int = 0
    last_visit_time: float = 0.0
    last_update_time: float = 0.0  # 마지막 업데이트 시간
    consolidated_bias: Optional[np.ndarray] = None  # Consolidated bias (통계적 유의성 검증 통과)
    consolidation_time: float = 0.0  # Consolidation 수행 시간
    
    def add_bias_to_history(self, bias: np.ndarray) -> None:
        """
        Bias 이력에 추가
        
        Args:
            bias: 새로운 bias 추정값
        """
        self.bias_history.append(bias.copy())
    
    def get_recent_biases(self, n: int) -> List[np.ndarray]:
        """
        최근 N회차의 bias 이력 반환
        
        Args:
            n: 반환할 회차 수
        
        Returns:
            최근 N회차의 bias 리스트
        """
        if len(self.bias_history) == 0:
            return []
        
        # 최근 N개 반환 (이력이 N개보다 적으면 모두 반환)
        recent = list(self.bias_history)[-n:]
        return recent


class ReplayConsolidation:
    """
    Replay/Consolidation Manager
    
    휴지기에 기억을 재검토하고 강화합니다.
    """
    
    def __init__(
        self,
        replay_threshold: float = 5.0,  # 5초 이상 휴지기
        consolidation_window: int = 10,  # 최근 10회차 평균
        significance_threshold: float = 0.001  # 통계적 유의성 임계값 (표준 편차)
    ):
        """
        Replay/Consolidation 초기화
        
        Args:
            replay_threshold: Replay 트리거 임계 시간 (초)
            consolidation_window: Consolidation 윈도우 크기 (회차 수)
            significance_threshold: 통계적 유의성 임계값 (표준 편차)
        """
        self.replay_threshold = replay_threshold
        self.consolidation_window = consolidation_window
        self.significance_threshold = significance_threshold
    
    def should_replay(
        self,
        last_update_time: float,
        current_time: float
    ) -> bool:
        """
        Replay를 실행해야 하는지 판단
        
        Args:
            last_update_time: 마지막 업데이트 시간
            current_time: 현재 시간
        
        Returns:
            Replay 실행 여부
        """
        return (current_time - last_update_time) > self.replay_threshold
    
    def is_significant(
        self,
        consolidated_bias: np.ndarray,
        recent_biases: List[np.ndarray]
    ) -> bool:
        """
        편향이 통계적으로 유의한지 검증
        
        여러 회차의 bias가 일관되면 진짜 편향, 아니면 노이즈로 판단
        
        Args:
            consolidated_bias: Consolidation된 bias (평균)
            recent_biases: 최근 회차의 bias 리스트
        
        Returns:
            통계적 유의성 여부
        """
        if len(recent_biases) < self.consolidation_window:
            return False  # 충분한 데이터가 없으면 유의하지 않음
        
        # 표준 편차 계산
        bias_array = np.array(recent_biases)
        std = np.std(bias_array, axis=0)
        
        # 모든 차원의 표준 편차가 임계값 이하이면 유의함
        return np.all(std < self.significance_threshold)
    
    def consolidate_place_memory(
        self,
        place_memory: 'PlaceMemoryWithHistory',
        current_time: float
    ) -> bool:
        """
        Place Memory Consolidation 수행
        
        최근 N회차의 bias를 평균하여 노이즈를 제거하고,
        통계적 유의성을 검증하여 장기 기억으로 고정합니다.
        
        Args:
            place_memory: Place Memory (이력 포함)
            current_time: 현재 시간
        
        Returns:
            Consolidation 성공 여부
        """
        # 충분한 방문 횟수가 없으면 Consolidation 불가
        if place_memory.visit_count < self.consolidation_window:
            return False
        
        # 최근 N회차의 bias 이력 가져오기
        recent_biases = place_memory.get_recent_biases(self.consolidation_window)
        
        if len(recent_biases) < self.consolidation_window:
            return False  # 충분한 이력이 없음
        
        # 최근 N회차의 bias를 평균하여 노이즈 제거
        consolidated_bias = np.mean(recent_biases, axis=0)
        
        # 통계적 유의성 검증
        if self.is_significant(consolidated_bias, recent_biases):
            # 진짜 편향으로 판단 → 장기 기억으로 고정
            place_memory.consolidated_bias = consolidated_bias.copy()
            place_memory.bias_estimate = consolidated_bias.copy()  # 장기 기억 업데이트
            place_memory.consolidation_time = current_time
            return True
        
        return False
    
    def replay_place_memory(
        self,
        place_memory: 'PlaceMemoryWithHistory',
        current_time: float
    ) -> bool:
        """
        Place Memory Replay 수행
        
        휴지기에 Place Memory를 재검토하고 Consolidation을 수행합니다.
        
        Args:
            place_memory: Place Memory (이력 포함)
            current_time: 현재 시간
        
        Returns:
            Consolidation 성공 여부
        """
        # 휴지기 감지
        if not self.should_replay(place_memory.last_update_time, current_time):
            return False  # 아직 휴지기가 아님
        
        # Consolidation 수행
        return self.consolidate_place_memory(place_memory, current_time)
    
    def replay_all_places(
        self,
        place_memory_dict: Dict[int, 'PlaceMemoryWithHistory'],
        current_time: float
    ) -> Dict[str, int]:
        """
        모든 Place Memory에 대해 Replay 수행
        
        Args:
            place_memory_dict: Place Memory 딕셔너리 (place_id → PlaceMemoryWithHistory)
            current_time: 현재 시간
        
        Returns:
            통계 정보 딕셔너리 (consolidated_count, total_count)
        """
        consolidated_count = 0
        total_count = len(place_memory_dict)
        
        for place_id, place_memory in place_memory_dict.items():
            if self.replay_place_memory(place_memory, current_time):
                consolidated_count += 1
        
        return {
            'consolidated_count': consolidated_count,
            'total_count': total_count,
            'consolidation_rate': consolidated_count / total_count if total_count > 0 else 0.0
        }


class ReplayConsolidationManager:
    """
    Replay/Consolidation 통합 관리자
    
    Place Cells와 Context Binder에 Replay/Consolidation을 적용합니다.
    """
    
    def __init__(
        self,
        replay_threshold: float = 5.0,
        consolidation_window: int = 10,
        significance_threshold: float = 0.001
    ):
        """
        Replay/Consolidation Manager 초기화
        
        Args:
            replay_threshold: Replay 트리거 임계 시간 (초)
            consolidation_window: Consolidation 윈도우 크기 (회차 수)
            significance_threshold: 통계적 유의성 임계값 (표준 편차)
        """
        self.replay = ReplayConsolidation(
            replay_threshold=replay_threshold,
            consolidation_window=consolidation_window,
            significance_threshold=significance_threshold
        )
    
    def update_place_memory_with_history(
        self,
        place_memory: 'PlaceMemoryWithHistory',
        bias: np.ndarray,
        current_time: float
    ) -> None:
        """
        Place Memory 업데이트 (이력 포함)
        
        Bias를 이력에 추가하고 업데이트 시간을 기록합니다.
        
        Args:
            place_memory: Place Memory (이력 포함)
            bias: 새로운 bias 추정값
            current_time: 현재 시간
        """
        # Bias 이력에 추가
        place_memory.add_bias_to_history(bias)
        
        # 업데이트 시간 기록
        place_memory.last_update_time = current_time
    
    def should_replay_all(self, last_update_time: float, current_time: float) -> bool:
        """
        모든 Place에 대해 Replay를 실행해야 하는지 판단
        
        Args:
            last_update_time: 마지막 업데이트 시간
            current_time: 현재 시간
        
        Returns:
            Replay 실행 여부
        """
        return self.replay.should_replay(last_update_time, current_time)
    
    def replay_all(
        self,
        place_memory_dict: Dict[int, 'PlaceMemoryWithHistory'],
        current_time: float
    ) -> Dict[str, int]:
        """
        모든 Place Memory에 대해 Replay 수행
        
        Args:
            place_memory_dict: Place Memory 딕셔너리
            current_time: 현재 시간
        
        Returns:
            통계 정보 딕셔너리
        """
        return self.replay.replay_all_places(place_memory_dict, current_time)


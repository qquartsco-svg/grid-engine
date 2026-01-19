"""
Universal Memory Interface
범용 기억 메모리 인터페이스 - 어떤 시스템에도 붙일 수 있는 해마 메모리

핵심 개념:
- 해마 메모리를 범용 모듈로 재정의
- 어떤 AI 시스템에도 붙일 수 있는 인터페이스
- 도메인 독립적 메모리 저장/검색/활용

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (Universal Memory Interface)
License: MIT License
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from .place_cells import PlaceCellManager, PlaceMemory
from .context_binder import ContextBinder, ContextMemory
from .learning_gate import LearningGate, LearningGateConfig
from .replay_consolidation import ReplayConsolidation
from .replay_buffer import ReplayBuffer, TrajectoryPoint


class UniversalMemory:
    """
    범용 기억 메모리 인터페이스
    
    어떤 시스템에도 붙일 수 있는 해마 메모리 모듈
    - LLM에 붙이기
    - 제어 시스템에 붙이기
    - 추천 시스템에 붙이기
    - 게임 AI에 붙이기
    - 등등...
    """
    
    def __init__(
        self,
        memory_dim: int = 5,  # 메모리 차원 (기본값: 5D)
        num_places: int = 1000,  # Place 수
        num_contexts: int = 10000,  # Context 수
        phase_wrap: float = 2.0 * np.pi,  # 위상 래핑
        quantization_level: int = 100  # 양자화 레벨
    ):
        """
        Universal Memory 초기화
        
        Args:
            memory_dim: 메모리 차원 (기본값: 5D)
            num_places: Place 수
            num_contexts: Context 수
            phase_wrap: 위상 래핑 값
            quantization_level: 양자화 레벨
        """
        self.memory_dim = memory_dim
        
        # 해마 구조 초기화
        self.place_manager = PlaceCellManager(
            num_places=num_places,
            phase_wrap=phase_wrap,
            quantization_level=quantization_level
        )
        
        self.context_binder = ContextBinder(num_contexts=num_contexts)
        
        self.learning_gate = LearningGate(
            config=LearningGateConfig(
                default_enabled=False,
                replay_only=True
            )
        )
        
        self.replay_consolidation = ReplayConsolidation(
            replay_threshold=1.0,
            consolidation_window=3,
            significance_threshold=0.1
        )
        
        self.replay_buffer = ReplayBuffer(
            max_size=10000,
            stable_window=10
        )
        
        # 상태 관리
        self.external_state: Dict[str, Any] = {}
        self.last_update_time: float = 0.0
        self.is_replay_phase: bool = False
    
    def store(
        self,
        key: Any,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        기억 저장 (범용 인터페이스)
        
        RAG의 문서 저장과 유사하지만, 상태/경향/습관을 저장
        
        Args:
            key: 기억 키 (위상 벡터, 상태 벡터, 또는 해시 가능한 값)
            value: 기억 값 (bias, 경향, 습관 등)
            context: 맥락 정보 (도메인 독립적)
            timestamp: 타임스탬프 (None이면 현재 시간)
        """
        # key를 위상 벡터로 변환
        phase_vector = self._key_to_phase_vector(key)
        
        # value를 bias로 변환
        bias = self._value_to_bias(value)
        
        # Context 설정
        if context is not None:
            self.external_state = context
        
        # Place ID 할당
        place_id = self.place_manager.get_place_id(phase_vector)
        
        # Context ID 할당
        context_id = self.context_binder.get_context_id(self.external_state)
        
        # Place Memory 업데이트
        place_memory = self.place_manager.get_place_memory(place_id)
        place_memory.update_bias(bias, learning_rate=0.1)
        place_memory.add_bias_to_history(bias)
        
        if place_memory.place_center is None:
            place_memory.place_center = phase_vector.copy()
        else:
            place_memory.update_place_center(phase_vector, learning_rate=0.05)
        
        # Context Memory 업데이트
        self.context_binder.update_context_memory(
            place_id=place_id,
            context_id=context_id,
            bias=bias,
            current_time=timestamp or 0.0,
            learning_rate=0.1
        )
        
        # Replay Buffer에 기록 (Online phase)
        if not self.is_replay_phase:
            self.replay_buffer.add_point(
                timestamp=timestamp or 0.0,
                phase_vector=phase_vector,
                current_state=phase_vector,  # 임시
                target_state=phase_vector,  # 임시
                error=bias,
                velocity=np.zeros(self.memory_dim),
                acceleration=np.zeros(self.memory_dim),
                place_id=place_id,
                context_id=context_id
            )
    
    def retrieve(
        self,
        query: Any,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        기억 검색 (범용 인터페이스)
        
        RAG의 문서 검색과 유사하지만, 상태/경향/습관을 검색
        
        Args:
            query: 검색 쿼리 (위상 벡터, 상태 벡터, 또는 해시 가능한 값)
            context: 맥락 정보
            top_k: 상위 K개 기억 반환
        
        Returns:
            기억 리스트 (각 기억은 Dict 형태)
        """
        # query를 위상 벡터로 변환
        phase_vector = self._key_to_phase_vector(query)
        
        # Context 설정
        if context is not None:
            self.external_state = context
        
        # Place ID 할당
        place_id = self.place_manager.get_place_id(phase_vector)
        
        # Context ID 할당
        context_id = self.context_binder.get_context_id(self.external_state)
        
        # Place Memory에서 bias 검색
        place_bias = self.place_manager.get_bias_estimate(
            phase_vector,
            use_blending=True,
            top_k=top_k,
            sigma=0.5
        )
        
        # Context Memory에서 bias 검색
        context_bias = self.context_binder.get_bias_estimate(place_id, context_id)
        
        # 결과 반환
        memories = []
        
        # Place 기반 기억
        place_memory = self.place_manager.get_place_memory(place_id)
        memories.append({
            "type": "place",
            "place_id": place_id,
            "bias": place_bias,
            "visit_count": place_memory.visit_count,
            "confidence": min(1.0, place_memory.visit_count / 10.0)
        })
        
        # Context 기반 기억
        context_memory = self.context_binder.get_context_memory(place_id, context_id)
        memories.append({
            "type": "context",
            "place_id": place_id,
            "context_id": context_id,
            "bias": context_bias,
            "visit_count": context_memory.visit_count,
            "confidence": min(1.0, context_memory.visit_count / 10.0)
        })
        
        return memories
    
    def augment(
        self,
        query: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        기억 증강 (범용 인터페이스)
        
        RAG의 컨텍스트 제공과 유사하지만, 상태/경향/습관을 제공
        
        Args:
            query: 검색 쿼리
            context: 맥락 정보
        
        Returns:
            증강된 컨텍스트 (Dict 형태)
        """
        # 기억 검색
        memories = self.retrieve(query, context)
        
        # 컨텍스트 구성
        augmented_context = {
            "query": query,
            "context": context or {},
            "memories": memories,
            "summary": self._summarize_memories(memories)
        }
        
        return augmented_context
    
    def _key_to_phase_vector(self, key: Any) -> np.ndarray:
        """
        키를 위상 벡터로 변환
        
        Args:
            key: 키 (위상 벡터, 상태 벡터, 또는 해시 가능한 값)
        
        Returns:
            위상 벡터
        """
        if isinstance(key, np.ndarray):
            # 이미 위상 벡터인 경우
            if key.shape[0] == self.memory_dim:
                return key.copy()
            else:
                # 차원이 다르면 패딩 또는 슬라이싱
                if key.shape[0] < self.memory_dim:
                    padded = np.zeros(self.memory_dim)
                    padded[:key.shape[0]] = key
                    return padded
                else:
                    return key[:self.memory_dim].copy()
        else:
            # 해시 가능한 값인 경우 해시하여 위상 벡터 생성
            hash_val = hash(str(key))
            phase_vector = np.array([
                (hash_val >> (i * 8)) % 256 / 256.0 * 2.0 * np.pi
                for i in range(self.memory_dim)
            ])
            return phase_vector
    
    def _value_to_bias(self, value: Any) -> np.ndarray:
        """
        값을 bias로 변환
        
        Args:
            value: 값 (bias, 경향, 습관 등)
        
        Returns:
            bias 벡터
        """
        if isinstance(value, np.ndarray):
            # 이미 배열인 경우
            if value.shape[0] == self.memory_dim:
                return value.copy()
            else:
                # 차원이 다르면 패딩 또는 슬라이싱
                if value.shape[0] < self.memory_dim:
                    padded = np.zeros(self.memory_dim)
                    padded[:value.shape[0]] = value
                    return padded
                else:
                    return value[:self.memory_dim].copy()
        elif isinstance(value, (int, float)):
            # 스칼라인 경우
            return np.full(self.memory_dim, float(value))
        elif isinstance(value, (list, tuple)):
            # 리스트/튜플인 경우
            arr = np.array(value)
            return self._value_to_bias(arr)
        else:
            # 기타 경우 0 벡터 반환
            return np.zeros(self.memory_dim)
    
    def _summarize_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        기억 요약
        
        Args:
            memories: 기억 리스트
        
        Returns:
            요약 정보
        """
        if not memories:
            return {
                "total_memories": 0,
                "average_confidence": 0.0,
                "has_memory": False
            }
        
        total_confidence = sum(m.get("confidence", 0.0) for m in memories)
        average_confidence = total_confidence / len(memories)
        
        return {
            "total_memories": len(memories),
            "average_confidence": average_confidence,
            "has_memory": average_confidence > 0.1
        }
    
    def replay(self, current_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Replay 수행 (기억 정제)
        
        Args:
            current_time: 현재 시간 (None이면 자동 계산)
        
        Returns:
            Replay 결과 통계
        """
        if current_time is None:
            current_time = self.last_update_time + 2.0  # 기본 2초 후
        
        current_time_s = current_time / 1000.0 if current_time > 1000 else current_time
        
        # Replay phase 시작
        self.is_replay_phase = True
        
        # 안정적인 구간 추출
        # ReplayBuffer의 get_stable_segments는 내부적으로 안정성 판단을 수행
        stable_segments = self.replay_buffer.get_stable_segments(min_segment_length=5)
        
        # Replay 수행
        consolidated_count = 0
        for segment in stable_segments:
            for point in segment:
                # Place Memory 업데이트
                place_memory = self.place_manager.get_place_memory(point.place_id)
                place_memory.update_bias(point.error, learning_rate=0.1)
                place_memory.add_bias_to_history(point.error)
                
                # Consolidation 수행
                if self.replay_consolidation.consolidate_place_memory(
                    place_memory, current_time_s
                ):
                    consolidated_count += 1
        
        # Replay phase 종료
        self.is_replay_phase = False
        
        # Replay Buffer 비우기
        self.replay_buffer.clear()
        
        return {
            "segments_processed": len(stable_segments),
            "consolidated_count": consolidated_count,
            "total_places": len(self.place_manager.place_memory)
        }


# 편의 함수: 범용 메모리 생성
def create_universal_memory(
    memory_dim: int = 5,
    num_places: int = 1000,
    num_contexts: int = 10000
) -> UniversalMemory:
    """
    범용 메모리 생성 (편의 함수)
    
    Args:
        memory_dim: 메모리 차원
        num_places: Place 수
        num_contexts: Context 수
    
    Returns:
        UniversalMemory 인스턴스
    """
    return UniversalMemory(
        memory_dim=memory_dim,
        num_places=num_places,
        num_contexts=num_contexts
    )


"""
Context Binder Module
Place + Context 조합으로 기억을 분리하여 오염을 방지하는 Context Binder 구현

핵심 개념:
- 같은 장소라도 공구/온도/작업 단계가 다르면 다른 기억으로 분리
- Place + Context 조합으로 독립적인 bias 저장
- 기억 오염 방지

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (Context Binder extension)
License: MIT License
"""

from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
import numpy as np
import hashlib


@dataclass
class ContextMemory:
    """
    Place + Context 조합의 기억 데이터 구조
    
    각 (place_id, context_id) 조합마다 독립적인 bias 추정값을 저장합니다.
    """
    place_id: int
    context_id: int
    bias_estimate: np.ndarray = field(default_factory=lambda: np.zeros(5))  # 5D bias [x, y, z, theta_a, theta_b]
    visit_count: int = 0
    last_visit_time: float = 0.0
    
    def update_bias(
        self,
        new_bias: np.ndarray,
        learning_rate: float = 0.1
    ) -> None:
        """
        Context별 bias 업데이트 (지수 이동 평균)
        
        수식: b_context = α·b_new + (1-α)·b_old
        
        Args:
            new_bias: 새로운 bias 추정값
            learning_rate: 학습률 α (기본값: 0.1)
        """
        if self.visit_count == 0:
            # 첫 방문: 새로운 bias 그대로 저장
            self.bias_estimate = new_bias.copy()
        else:
            # 이후 방문: 지수 이동 평균으로 업데이트
            self.bias_estimate = (
                learning_rate * new_bias +
                (1 - learning_rate) * self.bias_estimate
            )
        self.visit_count += 1


class ContextBinder:
    """
    Context Binder
    
    외부 상태(온도, 공구, 작업 단계 등)를 Context ID로 변환하고,
    Place + Context 조합으로 기억을 분리합니다.
    """
    
    def __init__(self, num_contexts: int = 10000):
        """
        Context Binder 초기화
        
        Args:
            num_contexts: 최대 Context 수 (기본값: 10000)
        """
        self.num_contexts = num_contexts
        
        # Context Memory 저장소: (place_id, context_id) → ContextMemory
        self.context_memory: Dict[Tuple[int, int], ContextMemory] = {}
    
    def get_context_id(
        self,
        external_state: Dict[str, Any]
    ) -> int:
        """
        외부 상태를 Context ID로 변환
        
        외부 상태의 예:
        - tool_type: 공구 타입 (예: "tool_A", "tool_B")
        - temperature: 온도 (예: 20.0, 25.0)
        - step_number: 작업 단계 (예: 0, 1, 2)
        - material: 재료 타입 (예: "aluminum", "steel")
        
        Args:
            external_state: 외부 상태 딕셔너리
        
        Returns:
            Context ID (0 ~ num_contexts-1)
        """
        # 외부 상태를 문자열로 변환하여 해시
        # 정렬하여 순서에 무관하게 동일한 상태는 동일한 Context ID 생성
        state_str = str(sorted(external_state.items()))
        
        # 해시 함수 적용 (MD5 사용)
        hash_obj = hashlib.md5(state_str.encode('utf-8'))
        context_hash = int(hash_obj.hexdigest(), 16)
        
        # 모듈로 연산으로 Context ID 생성
        context_id = context_hash % self.num_contexts
        
        return context_id
    
    def get_context_memory(
        self,
        place_id: int,
        context_id: int
    ) -> ContextMemory:
        """
        Context Memory 반환 (없으면 생성)
        
        Args:
            place_id: Place ID
            context_id: Context ID
        
        Returns:
            ContextMemory 객체
        """
        key = (place_id, context_id)
        
        if key not in self.context_memory:
            # 새로운 Context Memory 생성
            self.context_memory[key] = ContextMemory(
                place_id=place_id,
                context_id=context_id
            )
        
        return self.context_memory[key]
    
    def update_context_memory(
        self,
        place_id: int,
        context_id: int,
        bias: np.ndarray,
        current_time: float = 0.0,
        learning_rate: float = 0.1
    ) -> None:
        """
        Context Memory 업데이트
        
        Args:
            place_id: Place ID
            context_id: Context ID
            bias: 새로운 bias 추정값
            current_time: 현재 시간
            learning_rate: 학습률
        """
        context_memory = self.get_context_memory(place_id, context_id)
        
        # Bias 업데이트
        context_memory.update_bias(bias, learning_rate)
        
        # 방문 시간 업데이트
        context_memory.last_visit_time = current_time
    
    def get_bias_estimate(
        self,
        place_id: int,
        context_id: int
    ) -> np.ndarray:
        """
        Place + Context 조합의 bias 추정값 반환
        
        Args:
            place_id: Place ID
            context_id: Context ID
        
        Returns:
            Bias 추정값 (없으면 0 벡터)
        """
        key = (place_id, context_id)
        
        if key not in self.context_memory:
            return np.zeros(5)  # 초기값
        
        return self.context_memory[key].bias_estimate.copy()
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Context Binder 통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        if not self.context_memory:
            return {
                'num_contexts': 0,
                'total_visits': 0,
                'avg_visits_per_context': 0.0,
                'memory_size_bytes': 0
            }
        
        total_visits = sum(c.visit_count for c in self.context_memory.values())
        num_contexts = len(self.context_memory)
        
        # 메모리 사용량 추정 (대략적)
        # ContextMemory: 약 200 bytes per context
        memory_size_bytes = num_contexts * 200
        
        return {
            'num_contexts': num_contexts,
            'total_visits': total_visits,
            'avg_visits_per_context': total_visits / num_contexts if num_contexts > 0 else 0.0,
            'memory_size_bytes': memory_size_bytes,
            'memory_size_kb': memory_size_bytes / 1024.0
        }
    
    def clear_unused_contexts(
        self,
        min_visits: int = 2,
        max_age: float = 3600.0  # 1시간
    ) -> int:
        """
        사용되지 않는 Context Memory 정리
        
        Args:
            min_visits: 최소 방문 횟수 (이하이면 삭제)
            max_age: 최대 나이 (초, 초과이면 삭제)
        
        Returns:
            삭제된 Context 수
        """
        current_time = 0.0  # 실제로는 외부에서 전달받아야 함
        keys_to_delete = []
        
        for key, context_memory in self.context_memory.items():
            age = current_time - context_memory.last_visit_time
            
            if (context_memory.visit_count < min_visits or
                age > max_age):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.context_memory[key]
        
        return len(keys_to_delete)


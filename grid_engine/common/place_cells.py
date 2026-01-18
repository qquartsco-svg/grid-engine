"""
Place Cells Module
장소별 독립적인 기억(bias)을 저장하는 Place Cells 구현

핵심 개념:
- Grid = 좌표계 (연속적인 위상 공간)
- Place = 장소 ID (특정 위치를 고유하게 식별)
- Bias = 장소별 기억 (각 장소마다 독립적인 편향 추정값)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (Place Cells extension)
License: MIT License
"""

from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from collections import deque
import numpy as np
import math


@dataclass
class PlaceMemory:
    """
    Place별 기억 데이터 구조
    
    각 Place ID마다 독립적인 bias 추정값과 방문 정보를 저장합니다.
    """
    place_id: int
    bias_estimate: np.ndarray = field(default_factory=lambda: np.zeros(5))  # 5D bias [x, y, z, theta_a, theta_b]
    visit_count: int = 0
    last_visit_time: float = 0.0
    last_update_time: float = 0.0  # 마지막 업데이트 시간 (Replay용) ✨ NEW
    place_center: Optional[np.ndarray] = None  # Place Field 중심 위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b]
    bias_history: deque = field(default_factory=lambda: deque(maxlen=10))  # 최근 10회차 bias 이력 (Replay용) ✨ NEW
    consolidated_bias: Optional[np.ndarray] = None  # Consolidated bias (통계적 유의성 검증 통과) ✨ NEW
    consolidation_time: float = 0.0  # Consolidation 수행 시간 ✨ NEW
    
    def update_bias(
        self,
        new_bias: np.ndarray,
        learning_rate: float = 0.1
    ) -> None:
        """
        Place별 bias 업데이트 (지수 이동 평균)
        
        수식: b_place = α·b_new + (1-α)·b_old
        
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
    
    def add_bias_to_history(self, bias: np.ndarray) -> None:
        """
        Bias 이력에 추가 (Replay/Consolidation용)
        
        Args:
            bias: 새로운 bias 추정값
        """
        self.bias_history.append(bias.copy())
    
    def get_recent_biases(self, n: int) -> List[np.ndarray]:
        """
        최근 N회차의 bias 이력 반환 (Replay/Consolidation용)
        
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
    
    def update_place_center(
        self,
        phase_vector: np.ndarray,
        learning_rate: float = 0.05
    ) -> None:
        """
        Place Field 중심 업데이트
        
        수식: Φ_i^new = α·Φ_current + (1-α)·Φ_i^old
        
        Args:
            phase_vector: 현재 위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b]
            learning_rate: 중심 업데이트 학습률 (기본값: 0.05)
        """
        if self.place_center is None:
            # 첫 방문: 현재 위상을 중심으로 설정
            self.place_center = phase_vector.copy()
        else:
            # 이후 방문: 지수 이동 평균으로 업데이트
            self.place_center = (
                learning_rate * phase_vector +
                (1 - learning_rate) * self.place_center
            )


class PlaceCellManager:
    """
    Place Cells 관리자
    
    위상 공간을 Place ID로 변환하고, Place별 기억을 관리합니다.
    """
    
    def __init__(
        self,
        num_places: int = 1000,
        phase_wrap: float = 2.0 * math.pi,
        quantization_level: int = 100
    ):
        """
        Place Cell Manager 초기화
        
        Args:
            num_places: 최대 Place 수 (기본값: 1000)
            phase_wrap: 위상 wrapping 값 (기본값: 2π)
            quantization_level: 위상 공간 양자화 레벨 (기본값: 100)
        """
        self.num_places = num_places
        self.phase_wrap = phase_wrap
        self.quantization_level = quantization_level
        
        # Place Memory 저장소: place_id → PlaceMemory
        self.place_memory: Dict[int, PlaceMemory] = {}
        
        # Place Field 파라미터
        self.place_field_sigma: float = 0.1  # Place Field 폭 (rad)
        self.merge_threshold: float = 0.1  # Place Field 병합 임계 거리 (rad)
    
    def get_place_id(self, phase_vector: np.ndarray) -> int:
        """
        위상 벡터를 Place ID로 변환
        
        수식: place_id = hash(Φ) mod N
        
        Args:
            phase_vector: 위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b] (rad)
        
        Returns:
            Place ID (0 ~ num_places-1)
        """
        # 위상 공간 양자화
        # 위상 벡터를 정수 배열로 변환 (소수점 이하 자릿수 처리)
        phase_int = (phase_vector * self.quantization_level / self.phase_wrap).astype(int)
        
        # 해시 함수 적용
        # tuple로 변환하여 해시 가능하게 만듦
        place_hash = hash(tuple(phase_int))
        
        # 모듈로 연산으로 Place ID 생성
        place_id = place_hash % self.num_places
        
        # 음수 처리 (Python hash는 음수 가능)
        if place_id < 0:
            place_id = -place_id
        
        return place_id
    
    def torus_distance(
        self,
        phase1: np.ndarray,
        phase2: np.ndarray
    ) -> float:
        """
        토러스 거리 계산
        
        위상 공간은 토러스(T^n)이므로, 거리 측정 시 wrapping을 고려합니다.
        
        수식: d(Φ₁, Φ₂) = √(Σ min(||φ₁ᵢ - φ₂ᵢ||, 2π - ||φ₁ᵢ - φ₂ᵢ||)²)
        
        Args:
            phase1: 첫 번째 위상 벡터
            phase2: 두 번째 위상 벡터
        
        Returns:
            토러스 거리 (rad)
        """
        diff = phase1 - phase2
        
        # Wrapping: [-π, π] 범위로 정규화
        diff = diff - self.phase_wrap * np.round(diff / self.phase_wrap)
        
        # 유클리드 거리 계산
        distance = np.linalg.norm(diff)
        
        return distance
    
    def place_cell_activation(
        self,
        phase_vector: np.ndarray,
        place_center: np.ndarray,
        sigma: Optional[float] = None
    ) -> float:
        """
        Place Cell 활성화 강도 계산
        
        수식: a_i(Φ) = exp(-||Φ - Φ_i||² / 2σ²)
        
        Args:
            phase_vector: 현재 위상 벡터
            place_center: Place Field 중심 위상 벡터
            sigma: Place Field 폭 (None이면 기본값 사용)
        
        Returns:
            활성화 강도 [0, 1]
        """
        if sigma is None:
            sigma = self.place_field_sigma
        
        # 토러스 거리 계산
        distance = self.torus_distance(phase_vector, place_center)
        
        # Gaussian 활성화 함수
        activation = math.exp(-(distance ** 2) / (2 * sigma ** 2))
        
        return activation
    
    def get_place_memory(self, place_id: int) -> PlaceMemory:
        """
        Place Memory 반환 (없으면 생성)
        
        Args:
            place_id: Place ID
        
        Returns:
            PlaceMemory 객체
        """
        if place_id not in self.place_memory:
            # 새로운 Place Memory 생성
            self.place_memory[place_id] = PlaceMemory(place_id=place_id)
        
        return self.place_memory[place_id]
    
    def update_place_memory(
        self,
        place_id: int,
        phase_vector: np.ndarray,
        bias: np.ndarray,
        current_time: float = 0.0,
        learning_rate: float = 0.1
    ) -> None:
        """
        Place Memory 업데이트
        
        Args:
            place_id: Place ID
            phase_vector: 현재 위상 벡터
            bias: 새로운 bias 추정값
            current_time: 현재 시간
            learning_rate: 학습률
        """
        place_memory = self.get_place_memory(place_id)
        
        # Bias 업데이트
        place_memory.update_bias(bias, learning_rate)
        
        # Bias 이력에 추가 (Replay/Consolidation용) ✨ NEW
        place_memory.add_bias_to_history(bias)
        
        # Place Field 중심 업데이트
        place_memory.update_place_center(phase_vector, learning_rate=0.05)
        
        # 방문 시간 업데이트
        place_memory.last_visit_time = current_time
        place_memory.last_update_time = current_time  # Replay용 ✨ NEW
    
    def get_bias_estimate(
        self,
        phase_vector: np.ndarray
    ) -> np.ndarray:
        """
        현재 위상 벡터에 해당하는 Place의 bias 추정값 반환
        
        Args:
            phase_vector: 현재 위상 벡터
        
        Returns:
            Bias 추정값 (없으면 0 벡터)
        """
        place_id = self.get_place_id(phase_vector)
        place_memory = self.get_place_memory(place_id)
        
        return place_memory.bias_estimate.copy()
    
    def merge_nearby_places(
        self,
        distance_threshold: Optional[float] = None
    ) -> int:
        """
        가까운 Place Field들을 병합
        
        Args:
            distance_threshold: 병합 임계 거리 (None이면 기본값 사용)
        
        Returns:
            병합된 Place 수
        """
        if distance_threshold is None:
            distance_threshold = self.merge_threshold
        
        merged_count = 0
        place_ids = list(self.place_memory.keys())
        
        # 모든 Place 쌍에 대해 거리 계산
        for i, place_id1 in enumerate(place_ids):
            if place_id1 not in self.place_memory:
                continue
            
            place1 = self.place_memory[place_id1]
            if place1.place_center is None:
                continue
            
            for place_id2 in place_ids[i+1:]:
                if place_id2 not in self.place_memory:
                    continue
                
                place2 = self.place_memory[place_id2]
                if place2.place_center is None:
                    continue
                
                # 토러스 거리 계산
                distance = self.torus_distance(
                    place1.place_center,
                    place2.place_center
                )
                
                # 임계 거리 이하이면 병합
                if distance < distance_threshold:
                    # place_id1에 place_id2의 정보 병합
                    # Bias는 가중 평균 (방문 횟수 기준)
                    total_visits = place1.visit_count + place2.visit_count
                    if total_visits > 0:
                        weight1 = place1.visit_count / total_visits
                        weight2 = place2.visit_count / total_visits
                        place1.bias_estimate = (
                            weight1 * place1.bias_estimate +
                            weight2 * place2.bias_estimate
                        )
                    
                    # Place Field 중심도 가중 평균
                    place1.place_center = (
                        weight1 * place1.place_center +
                        weight2 * place2.place_center
                    )
                    
                    # 방문 횟수 합산
                    place1.visit_count += place2.visit_count
                    
                    # place_id2 삭제
                    del self.place_memory[place_id2]
                    merged_count += 1
        
        return merged_count
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Place Cells 통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        if not self.place_memory:
            return {
                'num_places': 0,
                'total_visits': 0,
                'avg_visits_per_place': 0.0,
                'memory_size_bytes': 0
            }
        
        total_visits = sum(p.visit_count for p in self.place_memory.values())
        num_places = len(self.place_memory)
        
        # 메모리 사용량 추정 (대략적)
        # PlaceMemory: 약 240 bytes per place
        memory_size_bytes = num_places * 240
        
        return {
            'num_places': num_places,
            'total_visits': total_visits,
            'avg_visits_per_place': total_visits / num_places if num_places > 0 else 0.0,
            'memory_size_bytes': memory_size_bytes,
            'memory_size_kb': memory_size_bytes / 1024.0
        }


"""
Cerebellum Demo
소뇌 엔진 사용 예시

해마 메모리와 소뇌 엔진의 통합 예시

Author: GNJz
Created: 2026-01-20
Made in GNJz
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from grid_engine.hippocampus import create_universal_memory
from grid_engine.cerebellum import create_cerebellum_engine, CerebellumConfig


def demo_hippocampus_cerebellum_integration():
    """해마-소뇌 통합 예시"""
    print("\n" + "=" * 70)
    print("예시: 해마-소뇌 통합")
    print("=" * 70)
    
    # 해마 메모리 생성
    memory = create_universal_memory(memory_dim=5)
    
    # 소뇌 엔진 생성 (해마 메모리 연결)
    cerebellum = create_cerebellum_engine(
        memory_dim=5,
        memory=memory
    )
    
    # 시나리오: 제어 시스템
    print("\n[시나리오] 제어 시스템에서 해마-소뇌 통합 사용")
    
    # 1. 해마에 기억 저장 (장소별 편향)
    position_1 = np.array([1.0, 0.5, 0.3, 10.0, 5.0])
    bias_1 = np.array([0.001, 0.002, 0.0, 0.0, 0.0])  # 열 변형으로 인한 편향
    
    memory.store(
        key=position_1,
        value=bias_1,
        context={"tool": "tool_A", "temperature": 25.0}
    )
    
    print(f"\n1. 해마에 기억 저장:")
    print(f"   Position: {position_1}")
    print(f"   Bias: {bias_1}")
    print(f"   Context: {{'tool': 'tool_A', 'temperature': 25.0}}")
    
    # 2. 제어 루프 시뮬레이션
    print(f"\n2. 제어 루프 시뮬레이션:")
    
    target_state = position_1.copy()
    current_state = position_1 + np.array([0.0005, 0.001, 0.0, 0.0, 0.0])  # 약간의 오차
    
    # 속도/가속도 (시뮬레이션)
    velocity = np.array([0.01, 0.02, 0.0, 0.0, 0.0])
    acceleration = np.array([0.001, 0.002, 0.0, 0.0, 0.0])
    
    # 소뇌 보정값 계산
    cerebellum_correction = cerebellum.compute_correction(
        current_state=current_state,
        target_state=target_state,
        velocity=velocity,
        acceleration=acceleration,
        context={"tool": "tool_A", "temperature": 25.0},
        dt=0.001
    )
    
    print(f"   Current State: {current_state}")
    print(f"   Target State: {target_state}")
    print(f"   Error: {target_state - current_state}")
    print(f"   Cerebellum Correction: {cerebellum_correction}")
    print(f"   Corrected Target: {target_state + cerebellum_correction}")
    
    # 3. 해마 기억 활용 확인
    memories = memory.retrieve(current_state, context={"tool": "tool_A"})
    if memories:
        print(f"\n3. 해마 기억 활용:")
        print(f"   Memory Bias: {memories[0]['bias']}")
        print(f"   Confidence: {memories[0]['confidence']:.2f}")
    
    # 4. 반복 루프 시뮬레이션 (Trial-to-Trial 보정)
    print(f"\n4. 반복 루프 시뮬레이션 (Trial-to-Trial 보정):")
    
    for i in range(5):
        # 약간의 노이즈 추가
        noise = np.random.normal(0, 0.0001, 5)
        current_state = target_state + noise
        
        # 소뇌 보정값 계산
        cerebellum_correction = cerebellum.compute_correction(
            current_state=current_state,
            target_state=target_state,
            velocity=velocity,
            acceleration=acceleration,
            context={"tool": "tool_A", "temperature": 25.0},
            dt=0.001
        )
        
        error_norm = np.linalg.norm(target_state - current_state)
        correction_norm = np.linalg.norm(cerebellum_correction)
        
        print(f"   Step {i+1}: Error Norm = {error_norm:.6f}, Correction Norm = {correction_norm:.6f}")
    
    print("\n✅ 해마-소뇌 통합 완료!")


def demo_predictive_feedforward():
    """Predictive Feedforward 예시"""
    print("\n" + "=" * 70)
    print("예시: Predictive Feedforward")
    print("=" * 70)
    
    # 소뇌 엔진 생성
    cerebellum = create_cerebellum_engine(memory_dim=5)
    
    # 시나리오: 빠른 움직임 예측
    print("\n[시나리오] 빠른 움직임에서 다음 순간의 오차 예측")
    
    current_state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    target_state = np.array([1.0, 1.0, 0.0, 0.0, 0.0])
    
    # 빠른 속도/가속도
    velocity = np.array([0.1, 0.1, 0.0, 0.0, 0.0])
    acceleration = np.array([0.01, 0.01, 0.0, 0.0, 0.0])
    
    # 소뇌 보정값 계산
    cerebellum_correction = cerebellum.compute_correction(
        current_state=current_state,
        target_state=target_state,
        velocity=velocity,
        acceleration=acceleration,
        dt=0.001
    )
    
    current_error = target_state - current_state
    print(f"   Current Error: {current_error}")
    print(f"   Velocity: {velocity}")
    print(f"   Acceleration: {acceleration}")
    print(f"   Cerebellum Correction: {cerebellum_correction}")
    print(f"   → 소뇌가 다음 순간의 오차를 예측하여 사전 보정합니다!")


def demo_variance_reduction():
    """Variance 감소 예시"""
    print("\n" + "=" * 70)
    print("예시: Variance 감소 (미세한 떨림 필터링)")
    print("=" * 70)
    
    # 소뇌 엔진 생성
    cerebellum = create_cerebellum_engine(memory_dim=5)
    
    # 시나리오: 노이즈가 있는 제어
    print("\n[시나리오] 노이즈가 있는 제어에서 Variance 감소")
    
    target_state = np.array([1.0, 0.5, 0.3, 10.0, 5.0])
    
    # 노이즈가 있는 상태 시뮬레이션
    for i in range(10):
        # 고주파 노이즈 추가
        noise = np.random.normal(0, 0.0005, 5)
        current_state = target_state + noise
        
        # 소뇌 보정값 계산
        cerebellum_correction = cerebellum.compute_correction(
            current_state=current_state,
            target_state=target_state,
            dt=0.001
        )
        
        error_norm = np.linalg.norm(target_state - current_state)
        correction_norm = np.linalg.norm(cerebellum_correction)
        
        print(f"   Step {i+1}: Error Norm = {error_norm:.6f}, Correction Norm = {correction_norm:.6f}")
    
    print("\n   → 소뇌가 고주파 노이즈를 필터링하여 부드러운 제어 신호를 생성합니다!")


def main():
    """메인 함수"""
    print("\n" + "=" * 70)
    print("Cerebellum Engine Demo")
    print("소뇌 엔진 - 기억을 즉각 행동으로 변환하는 계층")
    print("=" * 70)
    
    # 예시 실행
    demo_hippocampus_cerebellum_integration()
    demo_predictive_feedforward()
    demo_variance_reduction()
    
    print("\n" + "=" * 70)
    print("Demo 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()


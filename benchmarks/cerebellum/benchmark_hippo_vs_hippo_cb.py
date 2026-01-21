"""
Cerebellum 벤치마크: Hippo Only vs Hippo + Cerebellum

목적:
- 해마만 사용했을 때 vs 해마+소뇌 사용했을 때의 성능 비교
- Variance, Settling Time, Overshoot 지표 측정

Author: GNJz
Created: 2026-01-20
Made in GNJz
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from grid_engine.hippocampus import create_universal_memory
from grid_engine.cerebellum import create_cerebellum_engine, CerebellumConfig


class SimplePID:
    """간단한 PID 제어기 (시뮬레이션용)"""
    def __init__(self, kp=1.0, ki=0.1, kd=0.05):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = np.zeros(5)
        self.prev_error = None
    
    def compute(self, error, dt=0.001):
        """PID 제어 신호 계산"""
        if self.prev_error is None:
            self.prev_error = error.copy()
        
        # P
        p_term = self.kp * error
        
        # I
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # D
        d_term = self.kd * (error - self.prev_error) / dt
        self.prev_error = error.copy()
        
        return p_term + i_term + d_term


def run_simulation_hippo_only(
    target_trajectory,
    n_repeats=3,
    noise_std=0.001,
    dt=0.001
):
    """해마만 사용한 시뮬레이션"""
    memory = create_universal_memory(memory_dim=5)
    pid = SimplePID()
    
    errors = []
    states = []
    
    for repeat in range(n_repeats):
        current_state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        
        for t, target in enumerate(target_trajectory):
            # 노이즈 추가
            noise = np.random.normal(0, noise_std, 5)
            measured_state = current_state + noise
            
            # 해마에서 기억 검색
            memories = memory.retrieve(measured_state, {})
            if memories:
                memory_bias = memories[0]['bias']
            else:
                memory_bias = np.zeros(5)
            
            # 오차 계산 (해마 보정 포함)
            error = target - (measured_state + memory_bias)
            
            # PID 제어
            control = pid.compute(error, dt)
            
            # 상태 업데이트 (간단한 1차 시스템)
            current_state = current_state + control * dt
            
            # 해마에 기억 저장 (안정 구간에서만)
            if np.linalg.norm(error) < 0.01:
                memory.store(
                    key=measured_state,
                    value=error,
                    context={}
                )
            
            errors.append(error.copy())
            states.append(current_state.copy())
    
    return {
        'errors': np.array(errors),
        'states': np.array(states),
        'memory': memory
    }


def run_simulation_hippo_cerebellum(
    target_trajectory,
    n_repeats=3,
    noise_std=0.001,
    dt=0.001
):
    """해마 + 소뇌 사용한 시뮬레이션"""
    memory = create_universal_memory(memory_dim=5)
    cerebellum = create_cerebellum_engine(memory_dim=5, memory=memory)
    pid = SimplePID()
    
    errors = []
    states = []
    
    for repeat in range(n_repeats):
        current_state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        prev_state = current_state.copy()
        
        for t, target in enumerate(target_trajectory):
            # 노이즈 추가
            noise = np.random.normal(0, noise_std, 5)
            measured_state = current_state + noise
            
            # 해마에서 기억 검색
            memories = memory.retrieve(measured_state, {})
            if memories:
                memory_bias = memories[0]['bias']
            else:
                memory_bias = np.zeros(5)
            
            # 오차 계산 (해마 보정 포함)
            error = target - (measured_state + memory_bias)
            
            # 속도/가속도 추정
            if t > 0:
                velocity = (current_state - prev_state) / dt
                if t > 1:
                    prev_velocity = (prev_state - states[-2]) / dt if len(states) > 1 else np.zeros(5)
                    acceleration = (velocity - prev_velocity) / dt
                else:
                    acceleration = np.zeros(5)
            else:
                velocity = np.zeros(5)
                acceleration = np.zeros(5)
            
            # 소뇌 보정 계산
            cerebellum_correction = cerebellum.compute_correction(
                current_state=measured_state,
                target_state=target,
                velocity=velocity,
                acceleration=acceleration,
                context={},
                dt=dt
            )
            
            # PID 제어
            control = pid.compute(error, dt)
            
            # 최종 제어 신호 (PID + 소뇌)
            total_control = control + cerebellum_correction
            
            # 상태 업데이트
            current_state = current_state + total_control * dt
            prev_state = current_state.copy()
            
            # 해마에 기억 저장 (안정 구간에서만)
            if np.linalg.norm(error) < 0.01:
                memory.store(
                    key=measured_state,
                    value=error,
                    context={}
                )
            
            errors.append(error.copy())
            states.append(current_state.copy())
    
    return {
        'errors': np.array(errors),
        'states': np.array(states),
        'memory': memory,
        'cerebellum': cerebellum
    }


def calculate_metrics(errors, target_trajectory):
    """성능 지표 계산"""
    # Variance
    error_variance = np.var(errors, axis=0)
    total_variance = np.mean(error_variance)
    
    # RMS Error
    rms_error = np.sqrt(np.mean(errors**2))
    
    # Settling Time (목표의 2% 이내 도달 시간)
    target_norm = np.linalg.norm(target_trajectory[-1])
    epsilon = target_norm * 0.02
    
    settling_time = None
    for i, error in enumerate(errors):
        if np.linalg.norm(error) < epsilon:
            settling_time = i * 0.001  # dt = 0.001
            break
    
    if settling_time is None:
        settling_time = len(errors) * 0.001
    
    # Overshoot
    max_error = np.max(np.linalg.norm(errors, axis=1))
    overshoot = max(0, max_error - target_norm)
    
    return {
        'variance': total_variance,
        'rms_error': rms_error,
        'settling_time': settling_time,
        'overshoot': overshoot,
        'max_error': max_error
    }


def main():
    """메인 벤치마크 실행"""
    print("=" * 70)
    print("Cerebellum 벤치마크: Hippo Only vs Hippo + Cerebellum")
    print("=" * 70)
    print()
    
    # 타겟 궤적 생성 (간단한 직선 이동)
    n_steps = 200
    target_trajectory = []
    for i in range(n_steps):
        t = i / n_steps
        target = np.array([
            t * 1.0,  # x
            t * 0.5,  # y
            0.0,      # z
            t * 10.0, # theta_a
            t * 5.0   # theta_b
        ])
        target_trajectory.append(target)
    
    target_trajectory = np.array(target_trajectory)
    
    print("시뮬레이션 파라미터:")
    print(f"  - 궤적 길이: {n_steps} 스텝")
    print(f"  - 반복 횟수: 3회")
    print(f"  - 노이즈 표준편차: 0.001")
    print()
    
    # 1. Hippo Only
    print("Hippo Only 실행 중...")
    result_hippo = run_simulation_hippo_only(
        target_trajectory=target_trajectory,
        n_repeats=3,
        noise_std=0.001
    )
    metrics_hippo = calculate_metrics(result_hippo['errors'], target_trajectory)
    
    # 2. Hippo + Cerebellum
    print("Hippo + Cerebellum 실행 중...")
    result_hippo_cb = run_simulation_hippo_cerebellum(
        target_trajectory=target_trajectory,
        n_repeats=3,
        noise_std=0.001
    )
    metrics_hippo_cb = calculate_metrics(result_hippo_cb['errors'], target_trajectory)
    
    # 결과 출력
    print()
    print("=" * 70)
    print("벤치마크 결과")
    print("=" * 70)
    print()
    
    print("[Hippo Only]")
    print(f"  Variance: {metrics_hippo['variance']:.6f}")
    print(f"  RMS Error: {metrics_hippo['rms_error']:.6f}")
    print(f"  Settling Time: {metrics_hippo['settling_time']:.3f}s")
    print(f"  Overshoot: {metrics_hippo['overshoot']:.6f}")
    print(f"  Max Error: {metrics_hippo['max_error']:.6f}")
    print()
    
    print("[Hippo + Cerebellum]")
    print(f"  Variance: {metrics_hippo_cb['variance']:.6f}")
    print(f"  RMS Error: {metrics_hippo_cb['rms_error']:.6f}")
    print(f"  Settling Time: {metrics_hippo_cb['settling_time']:.3f}s")
    print(f"  Overshoot: {metrics_hippo_cb['overshoot']:.6f}")
    print(f"  Max Error: {metrics_hippo_cb['max_error']:.6f}")
    print()
    
    # 개선율 계산
    variance_reduction = (metrics_hippo['variance'] - metrics_hippo_cb['variance']) / metrics_hippo['variance'] * 100 if metrics_hippo['variance'] > 0 else 0
    rms_reduction = (metrics_hippo['rms_error'] - metrics_hippo_cb['rms_error']) / metrics_hippo['rms_error'] * 100 if metrics_hippo['rms_error'] > 0 else 0
    settling_reduction = (metrics_hippo['settling_time'] - metrics_hippo_cb['settling_time']) / metrics_hippo['settling_time'] * 100 if metrics_hippo['settling_time'] > 0 else 0
    overshoot_reduction = (metrics_hippo['overshoot'] - metrics_hippo_cb['overshoot']) / metrics_hippo['overshoot'] * 100 if metrics_hippo['overshoot'] > 0 else 0
    
    print("[개선율]")
    print(f"  Variance Reduction: {variance_reduction:+.1f}% (↓ {abs(variance_reduction):.1f}%)")
    print(f"  RMS Error Reduction: {rms_reduction:+.1f}% (↓ {abs(rms_reduction):.1f}%)")
    print(f"  Settling Time Reduction: {settling_reduction:+.1f}% (↓ {abs(settling_reduction):.1f}%)")
    print(f"  Overshoot Reduction: {overshoot_reduction:+.1f}% (↓ {abs(overshoot_reduction):.1f}%)")
    print()
    
    print("=" * 70)
    
    return {
        'hippo': metrics_hippo,
        'hippo_cb': metrics_hippo_cb,
        'improvements': {
            'variance': variance_reduction,
            'rms': rms_reduction,
            'settling_time': settling_reduction,
            'overshoot': overshoot_reduction
        }
    }


if __name__ == "__main__":
    main()


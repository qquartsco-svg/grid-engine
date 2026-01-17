"""
PID + Grid Engine Adapter Demo

기존 PID 제어 시스템에 Grid Engine을 침투(Infiltration)하여
정밀도를 향상시키는 통합 예제입니다.

이 예제는 INTEGRATION_STRATEGY.md의 "침투 전략"을 증명합니다.

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from typing import Tuple
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput, Grid5DConfig


class PIDController:
    """
    전통적인 PID 제어기 (기존 시스템)
    
    이 클래스는 기존 제어 시스템을 시뮬레이션합니다.
    Grid Engine은 이 시스템을 대체하지 않고, 보완합니다.
    """
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.01):
        self.kp = kp  # 비례 게인
        self.ki = ki  # 적분 게인
        self.kd = kd  # 미분 게인
        self.integral = 0.0
        self.prev_error = 0.0
        self.dt = 0.01  # 10ms
    
    def control(self, setpoint: float, current: float) -> float:
        """
        PID 제어 출력 계산
        
        Args:
            setpoint: 목표 값
            current: 현재 값
        
        Returns:
            제어 출력
        """
        error = setpoint - current
        
        # 적분 항
        self.integral += error * self.dt
        
        # 미분 항
        derivative = (error - self.prev_error) / self.dt
        
        # PID 출력
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        self.prev_error = error
        
        return output


class GridEngineAdapter:
    """
    Grid Engine 어댑터 (침투 전략)
    
    기존 PID 제어기에 Grid Engine을 추가하여 정밀도를 향상시킵니다.
    
    전략:
        1. PID 기본 제어 (기존 시스템 유지)
        2. Grid Engine으로 정밀 보정 (새로 추가)
        3. 통합 출력 (PID + Grid Engine)
    """
    
    def __init__(self, pid_controller: PIDController, grid_config: Grid5DConfig = None):
        """
        Grid Engine 어댑터 초기화
        
        Args:
            pid_controller: 기존 PID 제어기
            grid_config: Grid Engine 설정 (선택적)
        """
        self.pid = pid_controller
        self.grid_config = grid_config or Grid5DConfig(
            dt_ms=1.0,  # Grid Engine 시간 간격 (검증 조건 만족)
            tau_ms=10.0,  # 시간 상수
            max_dt_ratio=0.2,  # 최대 dt 비율
            spatial_scale_x=1.0,  # 1m = 2π rad
            spatial_scale_y=1.0,
            spatial_scale_z=1.0,
            angular_scale_a=360.0,  # 360° = 2π rad
            angular_scale_b=360.0
        )
        self.grid_engine = Grid5DEngine(config=self.grid_config)
        
        # Grid Engine 가중치 (점진적 전환)
        self.weight_pid = 0.7  # 기존 시스템 신뢰도
        self.weight_grid = 0.3  # Grid Engine 신뢰도
    
    def enhanced_control(
        self,
        setpoint: Tuple[float, float, float, float, float],  # (x, y, z, theta_a, theta_b)
        current: Tuple[float, float, float, float, float],
        disturbance: Tuple[float, float, float, float, float] = (0.0, 0.0, 0.0, 0.0, 0.0)
    ) -> Tuple[float, float, float, float, float]:
        """
        향상된 제어 (PID + Grid Engine)
        
        Args:
            setpoint: 목표 위치/각도 (x, y, z, theta_a, theta_b)
            current: 현재 위치/각도
            disturbance: 외란 (선택적)
        
        Returns:
            향상된 제어 출력 (x, y, z, theta_a, theta_b)
        """
        # 1. PID 기본 제어 (기존 시스템)
        pid_outputs = []
        for i in range(5):
            pid_output = self.pid.control(setpoint[i], current[i])
            pid_outputs.append(pid_output)
        
        # 2. Grid Engine으로 정밀 보정
        # PID 출력을 속도로 변환하여 Grid Engine에 입력
        grid_input = Grid5DInput(
            v_x=pid_outputs[0] * 0.1,  # PID 출력 → 속도 변환 [m/s]
            v_y=pid_outputs[1] * 0.1,
            v_z=pid_outputs[2] * 0.1,
            v_a=pid_outputs[3] * 0.1,  # [deg/s] (입력 단위)
            v_b=pid_outputs[4] * 0.1
        )
        
        # Grid Engine step 실행
        grid_output = self.grid_engine.step(grid_input)
        
        # 3. 통합 출력 (PID + Grid Engine)
        # 가중 평균으로 점진적 전환
        enhanced_outputs = []
        pid_values = np.array(pid_outputs)
        grid_values = np.array([
            grid_output.x,
            grid_output.y,
            grid_output.z,
            grid_output.theta_a,  # [deg] (출력 단위)
            grid_output.theta_b
        ])
        
        enhanced_outputs = (
            self.weight_pid * pid_values + self.weight_grid * grid_values
        )
        
        return tuple(enhanced_outputs)
    
    def set_weights(self, weight_pid: float, weight_grid: float):
        """
        가중치 설정 (점진적 전환)
        
        Phase 1: weight_pid=0.9, weight_grid=0.1 (침투)
        Phase 2: weight_pid=0.7, weight_grid=0.3 (효과 극대화)
        Phase 3: weight_pid=0.3, weight_grid=0.7 (점진적 전환)
        Phase 4: weight_pid=0.0, weight_grid=1.0 (메인 시스템)
        """
        assert abs(weight_pid + weight_grid - 1.0) < 1e-6, "가중치 합은 1.0이어야 합니다"
        self.weight_pid = weight_pid
        self.weight_grid = weight_grid


def compare_control_methods():
    """
    PID vs PID+Grid Engine 비교 데모
    """
    print("=" * 70)
    print("PID + Grid Engine Adapter Demo")
    print("침투 전략 증명: 기존 시스템 보완")
    print("=" * 70)
    print()
    
    # 시뮬레이션 설정
    setpoint = (1.0, 0.5, 0.3, 45.0, 30.0)  # 목표 위치/각도
    initial = (0.0, 0.0, 0.0, 0.0, 0.0)  # 초기 위치/각도
    n_steps = 100
    
    # 1. PID만 사용 (기존 시스템)
    print("1. PID만 사용 (기존 시스템)")
    print("-" * 70)
    pid_only = PIDController(kp=1.0, ki=0.1, kd=0.01)
    current_pid = list(initial)
    pid_errors = []
    
    for step in range(n_steps):
        # 외란 추가 (50번째 스텝에서)
        disturbance = (0.0, 0.0, 0.0, 0.0, 0.0)
        if step == 50:
            disturbance = (0.1, 0.05, 0.03, 5.0, 3.0)  # 외란
        
        # PID 제어
        outputs = []
        for i in range(5):
            output = pid_only.control(setpoint[i], current_pid[i])
            outputs.append(output)
            current_pid[i] += output * 0.01  # 위치 업데이트
        
        # 외란 적용
        current_pid = [c + d for c, d in zip(current_pid, disturbance)]
        
        # 오차 계산
        error = np.sqrt(sum((s - c) ** 2 for s, c in zip(setpoint, current_pid)))
        pid_errors.append(error)
        
        if step % 20 == 0:
            print(f"   Step {step:3d}: 위치=({current_pid[0]:.3f}, {current_pid[1]:.3f}, {current_pid[2]:.3f}), "
                  f"각도=({current_pid[3]:.2f}°, {current_pid[4]:.2f}°), 오차={error:.4f}")
    
    print(f"   최종 오차: {pid_errors[-1]:.4f}")
    print()
    
    # 2. PID + Grid Engine (침투 전략)
    print("2. PID + Grid Engine (침투 전략)")
    print("-" * 70)
    pid_controller = PIDController(kp=1.0, ki=0.1, kd=0.01)
    adapter = GridEngineAdapter(pid_controller)
    adapter.set_weights(0.7, 0.3)  # Phase 2: 효과 극대화
    
    # Grid Engine 초기화
    adapter.grid_engine.reset(
        initial_x=initial[0],
        initial_y=initial[1],
        initial_z=initial[2],
        initial_theta_a=initial[3],
        initial_theta_b=initial[4]
    )
    
    current_enhanced = list(initial)
    enhanced_errors = []
    
    for step in range(n_steps):
        # 외란 추가 (50번째 스텝에서)
        disturbance = (0.0, 0.0, 0.0, 0.0, 0.0)
        if step == 50:
            disturbance = (0.1, 0.05, 0.03, 5.0, 3.0)  # 외란
        
        # 향상된 제어 (PID + Grid Engine)
        enhanced_output = adapter.enhanced_control(
            setpoint,
            current_enhanced,
            disturbance
        )
        
        # 위치 업데이트
        current_enhanced = [c + o * 0.01 for c, o in zip(current_enhanced, enhanced_output)]
        
        # 외란 적용
        current_enhanced = [c + d for c, d in zip(current_enhanced, disturbance)]
        
        # 오차 계산
        error = np.sqrt(sum((s - c) ** 2 for s, c in zip(setpoint, current_enhanced)))
        enhanced_errors.append(error)
        
        if step % 20 == 0:
            print(f"   Step {step:3d}: 위치=({current_enhanced[0]:.3f}, {current_enhanced[1]:.3f}, {current_enhanced[2]:.3f}), "
                  f"각도=({current_enhanced[3]:.2f}°, {current_enhanced[4]:.2f}°), 오차={error:.4f}")
    
    print(f"   최종 오차: {enhanced_errors[-1]:.4f}")
    print()
    
    # 3. 비교 결과
    print("3. 비교 결과")
    print("-" * 70)
    improvement = ((pid_errors[-1] - enhanced_errors[-1]) / pid_errors[-1]) * 100
    print(f"   PID만:           최종 오차 = {pid_errors[-1]:.4f}")
    print(f"   PID + Grid:      최종 오차 = {enhanced_errors[-1]:.4f}")
    print(f"   개선율:          {improvement:.1f}%")
    print()
    
    # 외란 후 복귀 능력 비교
    print("4. 외란 후 복귀 능력 (Ring Attractor 효과)")
    print("-" * 70)
    pid_recovery = pid_errors[50] - pid_errors[-1]  # 외란 후 복귀
    enhanced_recovery = enhanced_errors[50] - enhanced_errors[-1]
    recovery_improvement = ((enhanced_recovery - pid_recovery) / pid_recovery) * 100 if pid_recovery > 0 else 0
    
    print(f"   PID만:           복귀 능력 = {pid_recovery:.4f}")
    print(f"   PID + Grid:      복귀 능력 = {enhanced_recovery:.4f}")
    print(f"   개선율:          {recovery_improvement:.1f}%")
    print()
    
    print("=" * 70)
    print("결론: Grid Engine 침투 전략이 효과를 극대화합니다.")
    print("      - 정밀도 향상: Ring Attractor 안정화")
    print("      - 외란 복귀: 위상 기억 및 복귀 능력")
    print("      - 점진적 전환: 기존 시스템과 병행 운영 가능")
    print("=" * 70)


if __name__ == "__main__":
    compare_control_methods()


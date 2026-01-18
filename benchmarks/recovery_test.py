"""
외란 복귀 비교 벤치마크 (Disturbance Recovery Benchmark)

Grid Engine의 핵심 가치를 증명하는 벤치마크:
- PID only vs PID + Grid Engine (Reference Stabilizer) 비교
- 외란 주입 후 복귀 시간 및 오차 측정

구조:
- 올바른 구조: Grid Engine을 Reference Stabilizer로 배치
- Reference Injection 방식: Target 보정 → PID 제어

시나리오:
1. 정상 궤적 실행
2. 외란 주입 (impulse disturbance)
3. PID only → 복귀 시간/오차 측정
4. PID + Grid (Reference Stabilizer) → 복귀 시간/오차 측정
5. 비교 결과 시각화

측정 지표:
- Settling Time (복귀 시간)
- RMS Position Error (위치 오차)
- Rotational Axis Stability (A/B 축 위상 안정성)

Author: GNJz
Created: 2026-01-20
Updated: 2026-01-20 (Reference Stabilizer 구조로 수정)
Made in GNJz
Version: v0.4.0-alpha
License: MIT License
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import matplotlib.pyplot as plt
import warnings
from typing import Tuple, List, Dict
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput, Grid5DConfig

# 한글 폰트 경고 억제
warnings.filterwarnings('ignore', category=UserWarning, message='.*Glyph.*missing from font.*')
plt.rcParams['font.family'] = 'DejaVu Sans'


class SuppressOutput:
    """출력 억제 컨텍스트 매니저"""
    def __enter__(self):
        import sys
        import os
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self
    def __exit__(self, *args):
        import sys
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr


class PIDController:
    """전통적인 PID 제어기 (기존 시스템)"""
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.01):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = np.zeros(5)  # 5D
        self.prev_error = np.zeros(5)
        self.dt = 0.01  # 10ms
    
    def control(self, setpoint: np.ndarray, current: np.ndarray) -> np.ndarray:
        """PID 제어 출력 계산 (5D)"""
        error = setpoint - current
        
        # 적분 업데이트
        self.integral += error * self.dt
        
        # 미분 계산
        derivative = (error - self.prev_error) / self.dt
        
        # PID 출력
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        self.prev_error = error.copy()
        return output
    
    def reset(self):
        """PID 상태 리셋"""
        self.integral = np.zeros(5)
        self.prev_error = np.zeros(5)


class GridEngineAdapter:
    """Grid Engine 어댑터 (Persistent Bias Estimator 구조)"""
    
    def __init__(self, setpoint: np.ndarray, pid_kp: float = 1.0, 
                 pid_ki: float = 0.1, pid_kd: float = 0.01):
        # Grid Engine 초기화 시 출력 억제
        with SuppressOutput():
            self.grid_engine = Grid5DEngine(
                config=Grid5DConfig(),
                initial_x=setpoint[0],
                initial_y=setpoint[1],
                initial_z=setpoint[2],
                initial_theta_a=setpoint[3],
                initial_theta_b=setpoint[4]
            )
            self.grid_engine.set_target(setpoint)
        self.pid = PIDController(kp=pid_kp, ki=pid_ki, kd=pid_kd)
        self.step_counter = 0
    
    def enhanced_control(self, setpoint: np.ndarray, current: np.ndarray, 
                        disturbance: np.ndarray = None) -> np.ndarray:
        """
        Reference Injection 방식으로 제어 (Persistent Bias Estimator)
        
        Grid Engine이 학습한 편향을 Target에 추가하여 외란 복귀를 보조합니다.
        """
        self.step_counter += 1
        
        # ✅ Grid Engine 상태 업데이트 (내부적으로 느린 주기로 필터링됨)
        self.grid_engine.update(current)
        
        # ✅ 학습된 편향 기반 Reference Correction 제공
        reference_correction = self.grid_engine.provide_reference()
        
        # ✅ 외란 복귀 시 동적 가중치 (오차가 클수록 더 강하게 보정)
        error_magnitude = np.linalg.norm(setpoint - current)
        correction_weight = min(1.0, 0.1 + error_magnitude * 5.0)
        
        # Reference Injection: Target 보정
        setpoint_corrected = setpoint + reference_correction * correction_weight
        
        # PID 제어 (보정된 setpoint 사용)
        pid_output = self.pid.control(setpoint_corrected, current)
        
        return pid_output


def run_recovery_test(
    setpoint: np.ndarray,
    n_steps: int = 200,
    disturbance_step: int = 50,
    disturbance_magnitude: np.ndarray = None
) -> Tuple[dict, dict]:
    """
    외란 복귀 테스트 실행
    
    Returns:
        pid_results: PID only 결과
        enhanced_results: PID + Grid 결과
    """
    if disturbance_magnitude is None:
        disturbance_magnitude = np.array([0.1, 0.05, 0.03, 5.0, 3.0])  # X, Y, Z, A, B
    
    # 초기 상태
    initial = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    
    # PID only 테스트
    pid_controller = PIDController()
    pid_current = initial.copy()
    pid_errors = []
    pid_positions = []
    
    # PID + Grid 테스트
    grid_adapter = GridEngineAdapter(setpoint)
    enhanced_current = initial.copy()
    enhanced_errors = []
    enhanced_positions = []
    
    for step in range(n_steps):
        # 외란 추가
        disturbance = np.zeros(5)
        if step == disturbance_step:
            disturbance = disturbance_magnitude.copy()
        
        # PID only
        pid_output = pid_controller.control(setpoint, pid_current)
        pid_current = pid_current + pid_output * 0.01 + disturbance
        pid_error = np.linalg.norm(setpoint - pid_current)
        pid_errors.append(pid_error)
        pid_positions.append(pid_current.copy())
        
        # PID + Grid
        enhanced_output = grid_adapter.enhanced_control(
            setpoint, enhanced_current, disturbance
        )
        enhanced_current = enhanced_current + enhanced_output * 0.01 + disturbance
        enhanced_error = np.linalg.norm(setpoint - enhanced_current)
        enhanced_errors.append(enhanced_error)
        enhanced_positions.append(enhanced_current.copy())
    
    # 결과 정리
    pid_errors_arr = np.array(pid_errors)
    enhanced_errors_arr = np.array(enhanced_errors)
    
    pid_results = {
        'errors': pid_errors_arr,
        'positions': np.array(pid_positions),
        'final_error': pid_errors[-1],
        'max_error': np.max(pid_errors_arr),
        'settling_time': calculate_settling_time(pid_errors, disturbance_step),
        'rms_error': np.sqrt(np.mean(pid_errors_arr[disturbance_step:] ** 2))
    }
    
    enhanced_results = {
        'errors': enhanced_errors_arr,
        'positions': np.array(enhanced_positions),
        'final_error': enhanced_errors[-1],
        'max_error': np.max(enhanced_errors_arr),
        'settling_time': calculate_settling_time(enhanced_errors, disturbance_step),
        'rms_error': np.sqrt(np.mean(enhanced_errors_arr[disturbance_step:] ** 2))
    }
    
    return pid_results, enhanced_results


def calculate_settling_time(errors: List[float], disturbance_step: int, 
                           threshold: float = 0.01) -> int:
    """복귀 시간 계산 (settling time)"""
    for i in range(disturbance_step, len(errors)):
        if errors[i] < threshold:
            return i - disturbance_step
    return len(errors) - disturbance_step  # 완전 복귀 못함


def plot_recovery_comparison(pid_results: dict, enhanced_results: dict, 
                            disturbance_step: int, output_file: str = None):
    """복귀 비교 그래프 생성"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # 1. 오차 비교
    ax1 = axes[0]
    steps = np.arange(len(pid_results['errors']))
    
    ax1.plot(steps, pid_results['errors'], 'r-', label='PID Only', linewidth=2)
    ax1.plot(steps, enhanced_results['errors'], 'b-', label='PID + Grid Engine', linewidth=2)
    ax1.axvline(x=disturbance_step, color='gray', linestyle='--', 
                label='Disturbance', linewidth=1)
    ax1.set_xlabel('Time Step', fontsize=12)
    ax1.set_ylabel('Position Error (RMS)', fontsize=12)
    ax1.set_title('Disturbance Recovery Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # 2. 위치 궤적 비교 (X, Y, Z)
    ax2 = axes[1]
    pid_pos = pid_results['positions']
    enhanced_pos = enhanced_results['positions']
    
    ax2.plot(steps, pid_pos[:, 0], 'r--', label='PID X', alpha=0.7)
    ax2.plot(steps, pid_pos[:, 1], 'r:', label='PID Y', alpha=0.7)
    ax2.plot(steps, pid_pos[:, 2], 'r-.', label='PID Z', alpha=0.7)
    ax2.plot(steps, enhanced_pos[:, 0], 'b-', label='Grid X', linewidth=2)
    ax2.plot(steps, enhanced_pos[:, 1], 'b-', label='Grid Y', linewidth=2)
    ax2.plot(steps, enhanced_pos[:, 2], 'b-', label='Grid Z', linewidth=2)
    ax2.axvline(x=disturbance_step, color='gray', linestyle='--', linewidth=1)
    ax2.set_xlabel('Time Step', fontsize=12)
    ax2.set_ylabel('Position [m]', fontsize=12)
    ax2.set_title('Position Trajectory Comparison', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10, ncol=3)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_file:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.savefig('benchmarks/recovery_comparison.png', dpi=300, bbox_inches='tight')
    
    plt.close()


def print_comparison_results(pid_results: dict, enhanced_results: dict):
    """비교 결과 출력 (간결한 테이블 형식)"""
    print("\n" + "=" * 80)
    print("외란 복귀 비교 결과 (Disturbance Recovery Comparison)")
    print("=" * 80)
    
    # 테이블 형식으로 출력
    print(f"{'지표':<30} {'PID Only':<20} {'PID + Grid':<20} {'개선율':<10}")
    print("-" * 80)
    
    # Settling Time
    st_pid = pid_results['settling_time']
    st_grid = enhanced_results['settling_time']
    st_improve = ((st_pid - st_grid) / st_pid * 100) if st_pid > 0 else 0.0
    print(f"{'복귀 시간 (steps)':<30} {st_pid:<20.1f} {st_grid:<20.1f} {st_improve:>+9.1f}%")
    
    # RMS Error
    rms_pid = pid_results['rms_error']
    rms_grid = enhanced_results['rms_error']
    rms_improve = ((rms_pid - rms_grid) / rms_pid * 100) if rms_pid > 0 else 0.0
    print(f"{'RMS 오차 (m)':<30} {rms_pid:<20.6f} {rms_grid:<20.6f} {rms_improve:>+9.1f}%")
    
    # Final Error
    final_pid = pid_results['final_error']
    final_grid = enhanced_results['final_error']
    final_improve = ((final_pid - final_grid) / final_pid * 100) if final_pid > 0 else 0.0
    print(f"{'최종 오차 (m)':<30} {final_pid:<20.6f} {final_grid:<20.6f} {final_improve:>+9.1f}%")
    
    # Max Error
    max_pid = pid_results['max_error']
    max_grid = enhanced_results['max_error']
    max_improve = ((max_pid - max_grid) / max_pid * 100) if max_pid > 0 else 0.0
    print(f"{'최대 오차 (m)':<30} {max_pid:<20.6f} {max_grid:<20.6f} {max_improve:>+9.1f}%")
    
    print("=" * 80)
    print("🔬 초기 결과 (검증 중) - 추가 검증 필요")
    print("=" * 80 + "\n")


def main():
    """메인 실행 함수"""
    # 목표 위치 설정 (5D)
    setpoint = np.array([1.0, 0.5, 0.3, 10.0, 5.0])  # X, Y, Z [m], A, B [deg]
    
    # 테스트 실행
    pid_results, enhanced_results = run_recovery_test(
        setpoint=setpoint,
        n_steps=200,
        disturbance_step=50,
        disturbance_magnitude=np.array([0.1, 0.05, 0.03, 5.0, 3.0])
    )
    
    # 결과 출력
    print_comparison_results(pid_results, enhanced_results)
    
    # 그래프 생성
    plot_recovery_comparison(
        pid_results, enhanced_results, 
        disturbance_step=50,
        output_file='benchmarks/recovery_comparison.png'
    )


if __name__ == "__main__":
    main()


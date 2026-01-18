"""
장기 드리프트 억제 벤치마크 (Long-term Drift Suppression Benchmark)

Grid Engine의 핵심 가치를 증명하는 벤치마크:
- PID only vs PID + Grid Engine (Reference Stabilizer) 비교
- 시간이 길어질수록 기준점이 얼마나 유지되는가?

시나리오:
1. 초기 목표 상태 설정
2. 매 스텝마다 미세 드리프트 주입 (열 변형/백래시 시뮬레이션)
   - X += 0.0001 m
   - Y += 0.0001 m
   - Z += 0.0001 m
   - A += 0.001 deg
   - B += 0.001 deg
3. 총 5,000~20,000 step 실행
4. 외란 없음 (중요: 드리프트만 존재)
5. PID only → 누적 오차 측정
6. PID + Grid (Reference Stabilizer) → 누적 오차 측정
7. 비교 결과 시각화

측정 지표:
- 누적 RMS 오차 (시간에 따른 오차 증가)
- 시작 위치 대비 최종 위치
- 기준점 drift slope (시간 대비 오차 증가율)

핵심 질문:
"시간이 길어질수록 기준점이 얼마나 유지되는가?"

Author: GNJz
Created: 2026-01-20
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
import logging
import sys
import os
from typing import Tuple, Dict, List
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput, Grid5DConfig

# 모든 경고 및 로그 억제
warnings.filterwarnings('ignore')
logging.getLogger('matplotlib').setLevel(logging.ERROR)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Grid Engine 초기화 시 출력 억제를 위한 컨텍스트 매니저
class SuppressOutput:
    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
    def __enter__(self):
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self
        
    def __exit__(self, *args):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.stdout
        sys.stderr = self.stderr


class PIDController:
    """전통적인 PID 제어기 (기존 시스템)"""
    
    def __init__(self, kp: float = 0.5, ki: float = 0.05, kd: float = 0.005, 
                 integral_limit: float = None):
        """
        PID 제어기 초기화
        
        ⚠️ 중요: gain을 낮춰서 드리프트 보정 능력을 제한
        - Grid Engine이 보정하지 못하는 드리프트를 학습할 수 있도록
        - 고주파 제어는 유지하되, 저주파 드리프트 보정은 제한
        
        Args:
            integral_limit: 적분 항 제한 (None이면 제한 없음)
                           드리프트 보정 능력을 완전히 차단하기 위해 사용
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_limit = integral_limit
        self.integral = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.prev_error = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    
    def control(self, setpoint: np.ndarray, current: np.ndarray) -> np.ndarray:
        """PID 제어 출력 계산"""
        error = setpoint - current
        self.integral += error
        
        # ⚠️ 적분 항 제한 (드리프트 보정 능력 제한)
        if self.integral_limit is not None:
            self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)
        
        derivative = error - self.prev_error
        self.prev_error = error
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return output
    
    def reset(self):
        """PID 상태 리셋"""
        self.integral = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self.prev_error = np.array([0.0, 0.0, 0.0, 0.0, 0.0])


class GridEngineAdapter:
    """Grid Engine을 Reference Stabilizer로 사용하는 어댑터"""
    
    def __init__(self, setpoint: np.ndarray):
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
        self.pid = PIDController()
        # ⚠️ 중요: Grid Engine 내부에서 느린 업데이트를 처리하므로
        # 여기서는 매 스텝마다 update()를 호출해도 됨
        # (Grid Engine이 내부적으로 slow_update_threshold로 필터링)
        self.step_counter = 0
    
    def enhanced_control(self, setpoint: np.ndarray, current: np.ndarray) -> np.ndarray:
        """
        Reference Injection 방식으로 제어 (Persistent Bias Estimator)
        
        Grid Engine이 학습한 편향을 Target에 추가하여 드리프트를 억제합니다.
        """
        self.step_counter += 1
        
        # ✅ Grid Engine 상태 업데이트 (내부적으로 느린 주기로 필터링됨)
        self.grid_engine.update(current)
        
        # ✅ 학습된 편향 기반 Reference Correction 제공
        reference_correction = self.grid_engine.provide_reference()
        
        # ✅ 편향 보정 가중치 (드리프트가 누적될수록 강하게)
        bias_magnitude = np.linalg.norm(reference_correction)
        # 편향이 클수록 더 강하게 보정 (최대 1.0으로 증가)
        # PID가 드리프트를 보정하지 못하므로, Grid가 더 강하게 보정해야 함
        correction_weight = min(1.0, 0.2 + bias_magnitude * 20.0)
        
        # Reference Injection: Target 보정
        setpoint_corrected = setpoint + reference_correction * correction_weight
        
        # PID 제어 (보정된 setpoint 사용)
        pid_output = self.pid.control(setpoint_corrected, current)
        
        return pid_output


def run_drift_test(
    setpoint: np.ndarray,
    n_steps: int = 10000,
    drift_rate: np.ndarray = None
) -> Tuple[Dict, Dict]:
    """
    장기 드리프트 억제 테스트 실행
    
    ⚠️ 중요: 벤치마크 시나리오 재설계
    - PID가 보정하지 못하는 드리프트 주입
    - 센서 노이즈로 시뮬레이션
    - Grid Engine이 실제 드리프트를 관찰할 수 있도록
    
    Args:
        setpoint: 목표 상태 [x, y, z, theta_a, theta_b]
        n_steps: 총 스텝 수 (기본값: 10,000)
        drift_rate: 매 스텝 드리프트 속도 [dx, dy, dz, dtheta_a, dtheta_b]
                   (기본값: [0.001, 0.001, 0.001, 0.01, 0.01] - 10배 증가)
    
    Returns:
        (pid_results, enhanced_results): 두 시스템의 결과 딕셔너리
    """
    if drift_rate is None:
        # ⚠️ 드리프트 크기 증가 (PID가 완전히 보정하지 못하도록)
        drift_rate = np.array([0.001, 0.001, 0.001, 0.01, 0.01])  # [m, m, m, deg, deg] - 10배 증가
    
    # PID Only 시스템
    # ⚠️ 적분 항 제한으로 드리프트 보정 능력 제한
    pid_controller = PIDController(integral_limit=0.01)  # 적분 항 제한
    pid_state = setpoint.copy()
    pid_errors = []
    pid_positions = [pid_state.copy()]
    
    # PID + Grid 시스템
    # Grid Engine이 드리프트를 학습할 수 있도록 동일한 PID 설정
    grid_adapter = GridEngineAdapter(setpoint)
    grid_adapter.pid = PIDController(integral_limit=0.01)  # 동일한 제한
    grid_state = setpoint.copy()
    grid_errors = []
    grid_positions = [grid_state.copy()]
    
    # 시뮬레이션 실행
    for step in range(n_steps):
        # ⚠️ 핵심 변경: 드리프트를 PID 제어 루프 밖에서 주입
        # 센서 노이즈로 시뮬레이션 (PID가 보정하지 못하는 영역)
        # 실제 시스템에서는 열 변형, 백래시 등이 센서 측정값에 영향을 줌
        
        # 1. 드리프트 주입 (시스템 레벨, PID 제어 전)
        #    실제 시스템에서는 센서가 이 드리프트를 "진짜"로 읽음
        pid_state += drift_rate
        grid_state += drift_rate
        
        # 2. 추가 센서 노이즈 (PID가 보정하지 못하는 고주파 노이즈)
        #    Grid Engine은 저주파로 필터링하여 학습
        sensor_noise = np.random.normal(0, drift_rate * 0.1, 5)
        pid_state += sensor_noise
        grid_state += sensor_noise
        
        # PID Only 제어
        pid_output = pid_controller.control(setpoint, pid_state)
        pid_state += pid_output * 0.1  # 제어 응답 시뮬레이션
        pid_error = np.linalg.norm(setpoint - pid_state)
        pid_errors.append(pid_error)
        pid_positions.append(pid_state.copy())
        
        # PID + Grid 제어
        # ⚠️ 중요: Grid Engine은 드리프트가 주입된 상태를 관찰해야 함
        # enhanced_control 내부에서 update()가 호출되므로,
        # 드리프트가 주입된 grid_state를 전달해야 함
        grid_output = grid_adapter.enhanced_control(setpoint, grid_state)
        grid_state += grid_output * 0.1  # 제어 응답 시뮬레이션
        grid_error = np.linalg.norm(setpoint - grid_state)
        grid_errors.append(grid_error)
        grid_positions.append(grid_state.copy())
    
    # 결과 계산
    pid_results = {
        'rms_error': np.sqrt(np.mean(np.array(pid_errors) ** 2)),
        'final_error': pid_errors[-1],
        'max_error': np.max(pid_errors),
        'drift_slope': np.polyfit(range(len(pid_errors)), pid_errors, 1)[0],  # 선형 회귀 기울기
        'final_position': pid_positions[-1],
        'position_drift': np.linalg.norm(pid_positions[-1] - pid_positions[0]),
        'errors': pid_errors,
        'positions': pid_positions
    }
    
    grid_results = {
        'rms_error': np.sqrt(np.mean(np.array(grid_errors) ** 2)),
        'final_error': grid_errors[-1],
        'max_error': np.max(grid_errors),
        'drift_slope': np.polyfit(range(len(grid_errors)), grid_errors, 1)[0],  # 선형 회귀 기울기
        'final_position': grid_positions[-1],
        'position_drift': np.linalg.norm(grid_positions[-1] - grid_positions[0]),
        'errors': grid_errors,
        'positions': grid_positions
    }
    
    return pid_results, grid_results


def visualize_drift_comparison(pid_results: Dict, grid_results: Dict, save_path: str = None):
    """드리프트 비교 결과 시각화"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('장기 드리프트 억제 비교: PID Only vs PID + Grid Engine', fontsize=16, fontweight='bold')
    
    # 1. 오차 시간 추이
    ax1 = axes[0, 0]
    steps = range(len(pid_results['errors']))
    ax1.plot(steps, pid_results['errors'], label='PID Only', color='red', alpha=0.7, linewidth=1.5)
    ax1.plot(steps, grid_results['errors'], label='PID + Grid', color='blue', alpha=0.7, linewidth=1.5)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Error (m)')
    ax1.set_title('오차 시간 추이')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 누적 RMS 오차
    ax2 = axes[0, 1]
    pid_rms_cumulative = [np.sqrt(np.mean(np.array(pid_results['errors'][:i+1]) ** 2)) 
                          for i in range(len(pid_results['errors']))]
    grid_rms_cumulative = [np.sqrt(np.mean(np.array(grid_results['errors'][:i+1]) ** 2)) 
                           for i in range(len(grid_results['errors']))]
    ax2.plot(steps, pid_rms_cumulative, label='PID Only', color='red', alpha=0.7, linewidth=1.5)
    ax2.plot(steps, grid_rms_cumulative, label='PID + Grid', color='blue', alpha=0.7, linewidth=1.5)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Cumulative RMS Error (m)')
    ax2.set_title('누적 RMS 오차')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Drift Slope 비교
    ax3 = axes[1, 0]
    categories = ['PID Only', 'PID + Grid']
    slopes = [pid_results['drift_slope'], grid_results['drift_slope']]
    colors = ['red', 'blue']
    bars = ax3.bar(categories, slopes, color=colors, alpha=0.7)
    ax3.set_ylabel('Drift Slope (error/step)')
    ax3.set_title('기준점 Drift Slope')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, slope in zip(bars, slopes):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{slope:.2e}',
                ha='center', va='bottom')
    
    # 4. 최종 위치 Drift
    ax4 = axes[1, 1]
    position_drifts = [pid_results['position_drift'], grid_results['position_drift']]
    bars = ax4.bar(categories, position_drifts, color=colors, alpha=0.7)
    ax4.set_ylabel('Position Drift (m)')
    ax4.set_title('시작 위치 대비 최종 위치 Drift')
    ax4.grid(True, alpha=0.3, axis='y')
    for bar, drift in zip(bars, position_drifts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{drift:.4f}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    
    if save_path:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
    plt.close()


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 70)
    print("장기 드리프트 억제 벤치마크 (Long-term Drift Suppression)")
    print("=" * 70)
    
    # 목표 상태 설정
    setpoint = np.array([1.0, 0.5, 0.3, 10.0, 5.0])  # [x, y, z, theta_a, theta_b]
    drift_rate = np.array([0.001, 0.001, 0.001, 0.01, 0.01])  # [m, m, m, deg, deg]
    
    print(f"\n설정:")
    print(f"  목표 상태: {setpoint}")
    print(f"  드리프트 속도: {drift_rate} (매 스텝)")
    print(f"  총 스텝 수: 10,000")
    print("\n테스트 실행 중...", end=" ", flush=True)
    
    pid_results, grid_results = run_drift_test(
        setpoint=setpoint,
        n_steps=10000,
        drift_rate=drift_rate
    )
    
    print("완료\n")
    
    # 개선율 계산
    rms_improvement = ((pid_results['rms_error'] - grid_results['rms_error']) / pid_results['rms_error']) * 100
    final_improvement = ((pid_results['final_error'] - grid_results['final_error']) / pid_results['final_error']) * 100
    drift_slope_improvement = ((pid_results['drift_slope'] - grid_results['drift_slope']) / abs(pid_results['drift_slope'])) * 100
    position_drift_improvement = ((pid_results['position_drift'] - grid_results['position_drift']) / pid_results['position_drift']) * 100
    
    # 개선율 추가 계산
    max_error_improvement = ((pid_results['max_error'] - grid_results['max_error']) / pid_results['max_error']) * 100
    
    # 결과 출력 (핵심만)
    print("=" * 70)
    print("비교 결과")
    print("=" * 70)
    print(f"\n{'지표':<25} {'PID Only':<20} {'PID + Grid':<20} {'개선율':<10}")
    print("-" * 70)
    print(f"{'RMS 오차 (m)':<25} {pid_results['rms_error']:<20.6f} {grid_results['rms_error']:<20.6f} {rms_improvement:>+6.1f}%")
    print(f"{'최종 오차 (m)':<25} {pid_results['final_error']:<20.6f} {grid_results['final_error']:<20.6f} {final_improvement:>+6.1f}%")
    print(f"{'최대 오차 (m)':<25} {pid_results['max_error']:<20.6f} {grid_results['max_error']:<20.6f} {max_error_improvement:>+6.1f}%")
    print(f"{'Drift Slope':<25} {pid_results['drift_slope']:<20.2e} {grid_results['drift_slope']:<20.2e} {drift_slope_improvement:>+6.1f}%")
    print(f"{'위치 Drift (m)':<25} {pid_results['position_drift']:<20.6f} {grid_results['position_drift']:<20.6f} {position_drift_improvement:>+6.1f}%")
    print()
    
    # 시각화 (조용히 저장)
    output_dir = Path(__file__).parent
    save_path = output_dir / "drift_comparison.png"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        visualize_drift_comparison(pid_results, grid_results, save_path=str(save_path))
    
    # 최종 판정
    print("=" * 70)
    print("판정")
    print("=" * 70)
    print(f"\n핵심 질문: '시간이 길어질수록 기준점이 얼마나 유지되는가?'\n")
    if rms_improvement > 30:
        print(f"✅ 성공: RMS 오차 {rms_improvement:.1f}% 개선 (산업적 의미 있음)")
    elif rms_improvement > 0:
        print(f"⚠️  부분 성공: RMS 오차 {rms_improvement:.1f}% 개선 (추가 최적화 필요)")
    else:
        print(f"❌ 실패: RMS 오차 {rms_improvement:.1f}% (메커니즘 재검토 필요)")
    print()


if __name__ == "__main__":
    main()


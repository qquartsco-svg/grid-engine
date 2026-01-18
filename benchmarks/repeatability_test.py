"""
반복 가공 정밀도 테스트 (Repeatability Precision Test)

Grid Engine의 핵심 가치를 증명하는 벤치마크:
- PID only vs PID + Grid Engine (Reference Stabilizer) 비교
- "PID는 순간 제어, Grid는 반복 정밀도"를 증명

시나리오:
1. 동일 궤적 100회 반복
2. 각 회차 종료 시 최종 위치 기록
3. PID only → 분산(σ) 및 최대 편차 측정
4. PID + Grid (Reference Stabilizer) → 분산(σ) 및 최대 편차 측정
5. 비교 결과 시각화

측정 지표:
- 첫 회 vs 100회 오차
- 분산 (σ)
- 최대 편차
- 반복 정밀도 (Repeatability)

핵심 질문:
"동일 가공을 반복할수록 정밀도가 얼마나 유지되는가?"

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
        
        # 적분 항 제한
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
        self.slow_update_cycle = 10  # 저주파 업데이트 주기 (10 스텝마다)
        self.step_counter = 0
    
    def enhanced_control(self, setpoint: np.ndarray, current: np.ndarray) -> np.ndarray:
        """Reference Injection 방식으로 제어"""
        self.step_counter += 1
        
        # 저주파 상태 업데이트
        if self.step_counter % self.slow_update_cycle == 0:
            self.grid_engine.update(current)
        
        # Reference Correction 제공
        reference_correction = self.grid_engine.provide_reference()
        
        # ✅ 편향 보정 가중치 (드리프트가 누적될수록 강하게)
        bias_magnitude = np.linalg.norm(reference_correction)
        # 편향이 클수록 더 강하게 보정 (최대 1.0)
        correction_weight = min(1.0, 0.2 + bias_magnitude * 20.0)
        
        # Reference Injection: Target 보정
        setpoint_corrected = setpoint + reference_correction * correction_weight
        
        # PID 제어 (보정된 setpoint 사용)
        pid_output = self.pid.control(setpoint_corrected, current)
        
        return pid_output
    
    def reset(self):
        """어댑터 상태 리셋"""
        self.pid.reset()
        self.step_counter = 0


def run_single_trajectory(
    setpoint: np.ndarray,
    n_steps: int = 100,
    use_grid: bool = False,
    grid_adapter: GridEngineAdapter = None
) -> np.ndarray:
    """
    단일 궤적 실행
    
    Args:
        setpoint: 목표 상태 [x, y, z, theta_a, theta_b]
        n_steps: 궤적 스텝 수
        use_grid: Grid Engine 사용 여부
        grid_adapter: Grid Engine 어댑터 (None이면 새로 생성)
    
    Returns:
        final_position: 최종 위치 [x, y, z, theta_a, theta_b]
    """
    if use_grid and grid_adapter is None:
        grid_adapter = GridEngineAdapter(setpoint)
    
    if not use_grid:
        pid_controller = PIDController(integral_limit=0.01)
    
    state = setpoint.copy()
    
    # 궤적 실행
    for step in range(n_steps):
        # 작은 노이즈 추가 (백래시 시뮬레이션)
        noise = np.random.normal(0, 0.0001, 5)  # [m, m, m, deg, deg]
        state += noise
        
        # 제어
        if use_grid:
            output = grid_adapter.enhanced_control(setpoint, state)
        else:
            output = pid_controller.control(setpoint, state)
        
        # 상태 업데이트
        state += output * 0.1
    
    return state


def run_repeatability_test(
    setpoint: np.ndarray,
    n_repeats: int = 100,
    trajectory_steps: int = 100
) -> Tuple[Dict, Dict]:
    """
    반복 가공 정밀도 테스트 실행
    
    Args:
        setpoint: 목표 상태 [x, y, z, theta_a, theta_b]
        n_repeats: 반복 횟수 (기본값: 100)
        trajectory_steps: 각 궤적의 스텝 수 (기본값: 100)
    
    Returns:
        (pid_results, enhanced_results): 두 시스템의 결과 딕셔너리
    """
    # PID Only 시스템
    pid_final_positions = []
    
    for repeat in range(n_repeats):
        final_pos = run_single_trajectory(
            setpoint=setpoint,
            n_steps=trajectory_steps,
            use_grid=False
        )
        pid_final_positions.append(final_pos)
    
    # PID + Grid 시스템
    grid_adapter = GridEngineAdapter(setpoint)
    grid_adapter.pid = PIDController(integral_limit=0.01)  # 동일한 PID 설정
    grid_final_positions = []
    
    for repeat in range(n_repeats):
        # ✅ Context Binder를 위한 외부 상태 설정 (각 반복마다) ✨ NEW
        external_state = {
            'step_number': repeat,  # 반복 횟수를 외부 상태로 설정
            'tool_type': 'default',
            'temperature': 20.0
        }
        grid_adapter.grid_engine.set_external_state(external_state)
        
        final_pos = run_single_trajectory(
            setpoint=setpoint,
            n_steps=trajectory_steps,
            use_grid=True,
            grid_adapter=grid_adapter
        )
        grid_final_positions.append(final_pos)
        # Grid Engine은 상태를 유지 (누적 편향 학습)
    
    # 결과 계산
    pid_final_positions = np.array(pid_final_positions)
    grid_final_positions = np.array(grid_final_positions)
    
    # 첫 회차 위치
    pid_first = pid_final_positions[0]
    grid_first = grid_final_positions[0]
    
    # 100회차 위치
    pid_last = pid_final_positions[-1]
    grid_last = grid_final_positions[-1]
    
    # 각 축별 분산 계산
    pid_variance = np.var(pid_final_positions, axis=0)
    grid_variance = np.var(grid_final_positions, axis=0)
    
    # 전체 분산 (5D)
    pid_total_variance = np.mean(pid_variance)
    grid_total_variance = np.mean(grid_variance)
    
    # 표준 편차 (σ)
    pid_std = np.sqrt(pid_total_variance)
    grid_std = np.sqrt(grid_total_variance)
    
    # 최대 편차 (각 회차의 최종 위치와 목표 위치의 차이)
    pid_errors = [np.linalg.norm(setpoint - pos) for pos in pid_final_positions]
    grid_errors = [np.linalg.norm(setpoint - pos) for pos in grid_final_positions]
    
    pid_max_deviation = np.max(pid_errors)
    grid_max_deviation = np.max(grid_errors)
    
    # 첫 회 vs 100회 오차
    pid_first_vs_last = np.linalg.norm(pid_first - pid_last)
    grid_first_vs_last = np.linalg.norm(grid_first - grid_last)
    
    pid_results = {
        'first_position': pid_first,
        'last_position': pid_last,
        'first_vs_last': pid_first_vs_last,
        'variance': pid_variance,
        'total_variance': pid_total_variance,
        'std': pid_std,
        'max_deviation': pid_max_deviation,
        'errors': pid_errors,
        'final_positions': pid_final_positions
    }
    
    grid_results = {
        'first_position': grid_first,
        'last_position': grid_last,
        'first_vs_last': grid_first_vs_last,
        'variance': grid_variance,
        'total_variance': grid_total_variance,
        'std': grid_std,
        'max_deviation': grid_max_deviation,
        'errors': grid_errors,
        'final_positions': grid_final_positions
    }
    
    return pid_results, grid_results


def visualize_repeatability_comparison(pid_results: Dict, grid_results: Dict, save_path: str = None):
    """반복 정밀도 비교 결과 시각화"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('반복 가공 정밀도 비교: PID Only vs PID + Grid Engine', fontsize=16, fontweight='bold')
    
    # 1. 각 회차별 최종 오차
    ax1 = axes[0, 0]
    repeats = range(len(pid_results['errors']))
    ax1.plot(repeats, pid_results['errors'], label='PID Only', color='red', alpha=0.7, linewidth=1.5)
    ax1.plot(repeats, grid_results['errors'], label='PID + Grid', color='blue', alpha=0.7, linewidth=1.5)
    ax1.set_xlabel('Repeat Number')
    ax1.set_ylabel('Final Error (m)')
    ax1.set_title('각 회차별 최종 오차')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 분산 비교 (각 축별)
    ax2 = axes[0, 1]
    axes_labels = ['X', 'Y', 'Z', 'A', 'B']
    x_pos = np.arange(len(axes_labels))
    width = 0.35
    ax2.bar(x_pos - width/2, np.sqrt(pid_results['variance']), width, 
            label='PID Only', color='red', alpha=0.7)
    ax2.bar(x_pos + width/2, np.sqrt(grid_results['variance']), width,
            label='PID + Grid', color='blue', alpha=0.7)
    ax2.set_xlabel('Axis')
    ax2.set_ylabel('Standard Deviation (σ)')
    ax2.set_title('각 축별 표준 편차')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(axes_labels)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. 최대 편차 비교
    ax3 = axes[1, 0]
    categories = ['PID Only', 'PID + Grid']
    max_deviations = [pid_results['max_deviation'], grid_results['max_deviation']]
    colors = ['red', 'blue']
    bars = ax3.bar(categories, max_deviations, color=colors, alpha=0.7)
    ax3.set_ylabel('Max Deviation (m)')
    ax3.set_title('최대 편차')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, dev in zip(bars, max_deviations):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{dev:.6f}',
                ha='center', va='bottom')
    
    # 4. 첫 회 vs 100회 오차
    ax4 = axes[1, 1]
    first_vs_last = [pid_results['first_vs_last'], grid_results['first_vs_last']]
    bars = ax4.bar(categories, first_vs_last, color=colors, alpha=0.7)
    ax4.set_ylabel('Position Drift (m)')
    ax4.set_title('첫 회차 vs 100회차 위치 Drift')
    ax4.grid(True, alpha=0.3, axis='y')
    for bar, drift in zip(bars, first_vs_last):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{drift:.6f}',
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
    print("반복 가공 정밀도 테스트 (Repeatability Test)")
    print("=" * 70)
    
    # 목표 상태 설정
    setpoint = np.array([1.0, 0.5, 0.3, 10.0, 5.0])  # [x, y, z, theta_a, theta_b]
    
    print(f"\n설정:")
    print(f"  목표 상태: {setpoint}")
    print(f"  반복 횟수: 100회")
    print(f"  각 궤적 스텝 수: 100")
    print("\n테스트 실행 중...", end=" ", flush=True)
    
    pid_results, grid_results = run_repeatability_test(
        setpoint=setpoint,
        n_repeats=100,
        trajectory_steps=100
    )
    
    print("완료\n")
    
    # 개선율 계산
    std_improvement = ((pid_results['std'] - grid_results['std']) / pid_results['std']) * 100
    max_dev_improvement = ((pid_results['max_deviation'] - grid_results['max_deviation']) / pid_results['max_deviation']) * 100
    drift_improvement = ((pid_results['first_vs_last'] - grid_results['first_vs_last']) / pid_results['first_vs_last']) * 100
    
    # 결과 출력 (핵심만)
    print("=" * 70)
    print("비교 결과")
    print("=" * 70)
    print(f"\n{'지표':<30} {'PID Only':<20} {'PID + Grid':<20} {'개선율':<10}")
    print("-" * 70)
    print(f"{'표준 편차 (σ) (m)':<30} {pid_results['std']:<20.6f} {grid_results['std']:<20.6f} {std_improvement:>+6.1f}%")
    print(f"{'최대 편차 (m)':<30} {pid_results['max_deviation']:<20.6f} {grid_results['max_deviation']:<20.6f} {max_dev_improvement:>+6.1f}%")
    print(f"{'첫 vs 마지막 Drift (m)':<30} {pid_results['first_vs_last']:<20.6f} {grid_results['first_vs_last']:<20.6f} {drift_improvement:>+6.1f}%")
    print()
    
    # 시각화 (조용히 저장)
    output_dir = Path(__file__).parent
    save_path = output_dir / "repeatability_comparison.png"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        visualize_repeatability_comparison(pid_results, grid_results, save_path=str(save_path))
    
    # 최종 판정
    print("=" * 70)
    print("판정")
    print("=" * 70)
    print(f"\n핵심 질문: '동일 가공을 반복할수록 정밀도가 얼마나 유지되는가?'\n")
    if std_improvement > 30:
        print(f"✅ 성공: 표준 편차 {std_improvement:.1f}% 개선 (CNC 업체가 이해하는 지표)")
    elif std_improvement > 0:
        print(f"⚠️  부분 성공: 표준 편차 {std_improvement:.1f}% 개선 (추가 최적화 필요)")
    else:
        print(f"❌ 실패: 표준 편차 {std_improvement:.1f}% (메커니즘 재검토 필요)")
    print()


if __name__ == "__main__":
    main()


"""
5축 위상 일관성 테스트 (5D Phase Coherence Test)

Grid Engine의 핵심 가치를 증명하는 벤치마크:
- PID only vs PID + Grid Engine (Reference Stabilizer) 비교
- "PID는 축별 제어, Grid는 5축 전체 위상 일관성"을 증명

시나리오:
1. 복합 움직임 시뮬레이션 (나선형 가공, 복잡한 로봇 관절 이동)
2. 5D 상태 벡터의 위상 거리 norm 계산
3. 축별이 아니라 상태 전체 거리 측정
4. PID only → 위상 일관성 측정
5. PID + Grid (Reference Stabilizer) → 위상 일관성 측정
6. 비교 결과 시각화

측정 지표:
- 5D 위상 거리 norm (상태 전체 일관성)
- 축별 위상 이탈 (Phase Lag)
- 위상 일관성 점수 (Phase Coherence Score)

핵심 질문:
"5개 축이 동시에 움직일 때 전체 자세 안정성이 얼마나 유지되는가?"

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
    
    def get_phase_state(self) -> np.ndarray:
        """Grid Engine의 위상 상태 반환"""
        state = self.grid_engine.get_state()
        return np.array([state.phi_x, state.phi_y, state.phi_z, state.phi_a, state.phi_b])


def compute_phase_distance(phase1: np.ndarray, phase2: np.ndarray, phase_wrap: float = 2.0 * np.pi) -> float:
    """
    5D 위상 거리 계산 (토러스 거리)
    
    Args:
        phase1: 첫 번째 위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b]
        phase2: 두 번째 위상 벡터 [phi_x, phi_y, phi_z, phi_a, phi_b]
        phase_wrap: 위상 래핑 값 (기본값: 2π)
    
    Returns:
        phase_distance: 5D 위상 거리 (norm)
    """
    # 각 축별 위상 차이 (토러스 거리)
    phase_diff = phase2 - phase1
    
    # 위상 래핑 고려 (최단 거리)
    phase_diff = np.mod(phase_diff + phase_wrap / 2, phase_wrap) - phase_wrap / 2
    
    # 5D 위상 거리 norm
    phase_distance = np.linalg.norm(phase_diff)
    
    return phase_distance


def compute_phase_coherence_score(phase_trajectory: List[np.ndarray], target_phase: np.ndarray) -> float:
    """
    위상 일관성 점수 계산
    
    Args:
        phase_trajectory: 위상 궤적 리스트
        target_phase: 목표 위상 벡터
    
    Returns:
        coherence_score: 위상 일관성 점수 (0~1, 높을수록 일관성 높음)
    """
    if len(phase_trajectory) == 0:
        return 0.0
    
    # 각 시점의 위상 거리 계산
    phase_distances = [compute_phase_distance(target_phase, phase) for phase in phase_trajectory]
    
    # 평균 위상 거리
    mean_distance = np.mean(phase_distances)
    
    # 위상 일관성 점수 (거리가 작을수록 높은 점수)
    # 정규화: 거리 0 → 점수 1, 거리 π → 점수 0
    coherence_score = np.exp(-mean_distance / np.pi)
    
    return coherence_score


def generate_complex_trajectory(n_steps: int = 500) -> List[np.ndarray]:
    """
    복합 움직임 궤적 생성 (나선형 가공 시뮬레이션)
    
    Args:
        n_steps: 스텝 수
    
    Returns:
        trajectory: 궤적 리스트 [x, y, z, theta_a, theta_b]
    """
    trajectory = []
    
    for step in range(n_steps):
        t = step / n_steps
        
        # 나선형 궤적
        x = 1.0 + 0.2 * np.cos(2 * np.pi * t * 3)
        y = 0.5 + 0.2 * np.sin(2 * np.pi * t * 3)
        z = 0.3 + 0.1 * t
        theta_a = 10.0 + 30.0 * np.sin(2 * np.pi * t * 2)
        theta_b = 5.0 + 20.0 * np.cos(2 * np.pi * t * 2)
        
        trajectory.append(np.array([x, y, z, theta_a, theta_b]))
    
    return trajectory


def run_phase_coherence_test(
    trajectory: List[np.ndarray],
    use_grid: bool = False
) -> Tuple[Dict, List[np.ndarray]]:
    """
    5축 위상 일관성 테스트 실행
    
    Args:
        trajectory: 목표 궤적 리스트
        use_grid: Grid Engine 사용 여부
    
    Returns:
        (results, phase_trajectory): 결과 딕셔너리와 위상 궤적
    """
    if use_grid:
        grid_adapter = GridEngineAdapter(trajectory[0])
        grid_adapter.pid = PIDController(integral_limit=0.01)
    else:
        pid_controller = PIDController(integral_limit=0.01)
    
    state = trajectory[0].copy()
    phase_trajectory = []
    phase_distances = []
    position_errors = []
    
    # Grid Engine의 위상 상태를 가져오기 위한 변환
    config = Grid5DConfig()
    from grid_engine.dimensions.dim5d.projector_5d import Coordinate5DProjector
    projector = Coordinate5DProjector(config)
    
    # 초기 목표 위상
    target_phase_initial = np.array(projector.coordinate_to_phase(
        trajectory[0][0], trajectory[0][1], trajectory[0][2],
        trajectory[0][3], trajectory[0][4]
    ))
    
    # 궤적 실행
    for step, target in enumerate(trajectory):
        # 제어
        if use_grid:
            output = grid_adapter.enhanced_control(target, state)
            # Grid Engine의 위상 상태 가져오기
            phase_state = grid_adapter.get_phase_state()
        else:
            output = pid_controller.control(target, state)
            # PID는 위상 상태가 없으므로 현재 상태를 위상으로 변환
            phi_x, phi_y, phi_z, phi_a, phi_b = projector.coordinate_to_phase(
                state[0], state[1], state[2], state[3], state[4]
            )
            phase_state = np.array([phi_x, phi_y, phi_z, phi_a, phi_b])
        
        # 상태 업데이트
        state += output * 0.1
        
        # 목표 위상 계산
        target_phi_x, target_phi_y, target_phi_z, target_phi_a, target_phi_b = projector.coordinate_to_phase(
            target[0], target[1], target[2], target[3], target[4]
        )
        target_phase = np.array([target_phi_x, target_phi_y, target_phi_z, target_phi_a, target_phi_b])
        
        # 위상 거리 계산
        phase_distance = compute_phase_distance(target_phase, phase_state)
        phase_distances.append(phase_distance)
        
        # 위치 오차 계산
        position_error = np.linalg.norm(target - state)
        position_errors.append(position_error)
        
        phase_trajectory.append(phase_state)
    
    # 위상 일관성 점수 계산
    coherence_score = compute_phase_coherence_score(phase_trajectory, target_phase_initial)
    
    results = {
        'phase_distances': phase_distances,
        'position_errors': position_errors,
        'coherence_score': coherence_score,
        'mean_phase_distance': np.mean(phase_distances),
        'std_phase_distance': np.std(phase_distances),
        'max_phase_distance': np.max(phase_distances),
        'mean_position_error': np.mean(position_errors),
        'std_position_error': np.std(position_errors),
        'max_position_error': np.max(position_errors)
    }
    
    return results, phase_trajectory


def visualize_phase_coherence_comparison(pid_results: Dict, grid_results: Dict, save_path: str = None):
    """위상 일관성 비교 결과 시각화"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('5축 위상 일관성 비교: PID Only vs PID + Grid Engine', fontsize=16, fontweight='bold')
    
    # 1. 위상 거리 시간 추이
    ax1 = axes[0, 0]
    steps = range(len(pid_results['phase_distances']))
    ax1.plot(steps, pid_results['phase_distances'], label='PID Only', color='red', alpha=0.7, linewidth=1.5)
    ax1.plot(steps, grid_results['phase_distances'], label='PID + Grid', color='blue', alpha=0.7, linewidth=1.5)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Phase Distance (rad)')
    ax1.set_title('5D 위상 거리 시간 추이')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 위상 일관성 점수 비교
    ax2 = axes[0, 1]
    categories = ['PID Only', 'PID + Grid']
    coherence_scores = [pid_results['coherence_score'], grid_results['coherence_score']]
    colors = ['red', 'blue']
    bars = ax2.bar(categories, coherence_scores, color=colors, alpha=0.7)
    ax2.set_ylabel('Phase Coherence Score')
    ax2.set_title('위상 일관성 점수 (0~1, 높을수록 일관성 높음)')
    ax2.set_ylim([0, 1])
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, score in zip(bars, coherence_scores):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{score:.4f}',
                ha='center', va='bottom')
    
    # 3. 평균 위상 거리 비교
    ax3 = axes[1, 0]
    mean_distances = [pid_results['mean_phase_distance'], grid_results['mean_phase_distance']]
    bars = ax3.bar(categories, mean_distances, color=colors, alpha=0.7)
    ax3.set_ylabel('Mean Phase Distance (rad)')
    ax3.set_title('평균 위상 거리')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, dist in zip(bars, mean_distances):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{dist:.4f}',
                ha='center', va='bottom')
    
    # 4. 위치 오차 비교
    ax4 = axes[1, 1]
    mean_errors = [pid_results['mean_position_error'], grid_results['mean_position_error']]
    bars = ax4.bar(categories, mean_errors, color=colors, alpha=0.7)
    ax4.set_ylabel('Mean Position Error (m)')
    ax4.set_title('평균 위치 오차')
    ax4.grid(True, alpha=0.3, axis='y')
    for bar, err in zip(bars, mean_errors):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{err:.6f}',
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
    print("5축 위상 일관성 테스트 (5D Phase Coherence Test)")
    print("=" * 70)
    
    # 복합 움직임 궤적 생성
    print("\n궤적 생성 중...", end=" ", flush=True)
    trajectory = generate_complex_trajectory(n_steps=500)
    print(f"완료 ({len(trajectory)} steps)")
    
    # 테스트 실행
    print("\n테스트 실행 중...", end=" ", flush=True)
    pid_results, _ = run_phase_coherence_test(trajectory, use_grid=False)
    grid_results, _ = run_phase_coherence_test(trajectory, use_grid=True)
    print("완료\n")
    
    # 개선율 계산
    coherence_improvement = ((grid_results['coherence_score'] - pid_results['coherence_score']) / pid_results['coherence_score']) * 100
    phase_dist_improvement = ((pid_results['mean_phase_distance'] - grid_results['mean_phase_distance']) / pid_results['mean_phase_distance']) * 100
    
    # 결과 출력 (핵심만)
    print("=" * 70)
    print("비교 결과")
    print("=" * 70)
    print(f"\n{'지표':<30} {'PID Only':<20} {'PID + Grid':<20} {'개선율':<10}")
    print("-" * 70)
    print(f"{'위상 일관성 점수':<30} {pid_results['coherence_score']:<20.4f} {grid_results['coherence_score']:<20.4f} {coherence_improvement:>+6.1f}%")
    print(f"{'평균 위상 거리 (rad)':<30} {pid_results['mean_phase_distance']:<20.4f} {grid_results['mean_phase_distance']:<20.4f} {phase_dist_improvement:>+6.1f}%")
    print(f"{'표준 편차 (rad)':<30} {pid_results['std_phase_distance']:<20.4f} {grid_results['std_phase_distance']:<20.4f} {'-':>10}")
    print(f"{'최대 위상 거리 (rad)':<30} {pid_results['max_phase_distance']:<20.4f} {grid_results['max_phase_distance']:<20.4f} {'-':>10}")
    print()
    
    # 시각화 (조용히 저장)
    output_dir = Path(__file__).parent
    save_path = output_dir / "phase_coherence_comparison.png"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        visualize_phase_coherence_comparison(pid_results, grid_results, save_path=str(save_path))
    
    # 최종 판정
    print("=" * 70)
    print("판정")
    print("=" * 70)
    print(f"\n핵심 질문: '5개 축이 동시에 움직일 때 전체 자세 안정성이 얼마나 유지되는가?'\n")
    if coherence_improvement > 30:
        print(f"✅ 성공: 위상 일관성 {coherence_improvement:.1f}% 개선 (5축 동기 안정화 증명)")
    elif coherence_improvement > 0:
        print(f"⚠️  부분 성공: 위상 일관성 {coherence_improvement:.1f}% 개선 (추가 최적화 필요)")
    else:
        print(f"❌ 실패: 위상 일관성 {coherence_improvement:.1f}% (메커니즘 재검토 필요)")
    print()


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Grid Engine 시각화 데모
2D 궤적 시각화 및 위상 변화 그래프

주의: 이 데모는 "관측용 좌표 투영"을 보여줍니다.
Grid Engine 자체는 내부 위상 상태만 유지하며,
좌표 투영은 상위 시스템(이 데모)의 책임입니다.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine import GridEngine, GridInput, GridEngineConfig


def phase_to_world_coordinate(phi_x: float, phi_y: float, config: GridEngineConfig) -> tuple:
    """
    위상 → 세계 좌표 변환 (관측용)
    
    이 함수는 Grid Engine 외부에서 실행됩니다.
    Grid Engine은 위상만 유지하고, 좌표 투영은 관측자의 책임입니다.
    
    Args:
        phi_x: X 방향 위상 [rad]
        phi_y: Y 방향 위상 [rad]
        config: Grid Engine 설정
    
    Returns:
        (x, y) 세계 좌표
    """
    # Grid spacing (격자 간격)
    # 기본값: 2π rad = 1.0 m
    grid_spacing = config.spatial_scale_x  # [m/rad]
    
    x = phi_x * (grid_spacing / config.phase_wrap)
    y = phi_y * (grid_spacing / config.phase_wrap)
    
    return x, y


def main():
    """Grid Engine 시각화 데모"""
    print("=" * 60)
    print("Grid Engine 시각화 데모")
    print("=" * 60)
    print()
    print("주의: Grid Engine은 내부 위상 상태만 유지합니다.")
    print("좌표 투영은 이 데모(관측자)의 책임입니다.")
    print()
    
    # Grid Engine 초기화
    print("1. Grid Engine 초기화...")
    config = GridEngineConfig(
        dt_ms=0.5,  # 더 큰 시간 간격으로 변화를 명확히 (안정 조건 만족)
        spatial_scale_x=10.0,  # 더 큰 스케일로 시각화
        spatial_scale_y=10.0
    )
    engine = GridEngine(initial_x=0.0, initial_y=0.0, config=config)
    state = engine.get_state()
    print(f"   초기 위상: ({state.phi_x:.3f}, {state.phi_y:.3f}) rad")
    print()
    
    # 궤적 데이터 저장
    trajectory = []
    phases_x = []
    phases_y = []
    velocities_x = []
    velocities_y = []
    times = []
    
    # 1단계: 일정한 속도로 이동 (v_x=1.0, v_y=0.0)
    print("2. 일정한 속도로 이동 (v_x=1.0, v_y=0.0)...")
    inp = GridInput(v_x=1.0, v_y=0.0)
    
    for i in range(100):  # 100 스텝 = 100ms
        output = engine.step(inp)
        state = engine.get_state()
        
        # 위상 → 좌표 변환 (관측자 책임)
        x, y = phase_to_world_coordinate(state.phi_x, state.phi_y, config)
        
        trajectory.append((x, y))
        phases_x.append(state.phi_x)
        phases_y.append(state.phi_y)
        velocities_x.append(state.v_x)
        velocities_y.append(state.v_y)
        times.append(state.t_ms)
    
    print(f"   최종 위치 (관측): ({trajectory[-1][0]:.3f}, {trajectory[-1][1]:.3f}) m")
    print(f"   최종 위상 (내부): ({phases_x[-1]:.3f}, {phases_y[-1]:.3f}) rad")
    print()
    
    # 2단계: 가속도를 포함한 이동
    print("3. 가속도를 포함한 이동 (a_x=0.1, a_y=0.0)...")
    inp_accel = GridInput(v_x=0.0, v_y=0.0, a_x=0.1, a_y=0.0)
    
    for i in range(100):  # 추가 100 스텝
        output = engine.step(inp_accel)
        state = engine.get_state()
        
        # 위상 → 좌표 변환
        x, y = phase_to_world_coordinate(state.phi_x, state.phi_y, config)
        
        trajectory.append((x, y))
        phases_x.append(state.phi_x)
        phases_y.append(state.phi_y)
        velocities_x.append(state.v_x)
        velocities_y.append(state.v_y)
        times.append(state.t_ms)
    
    print(f"   최종 위치 (관측): ({trajectory[-1][0]:.3f}, {trajectory[-1][1]:.3f}) m")
    print(f"   최종 위상 (내부): ({phases_x[-1]:.3f}, {phases_y[-1]:.3f}) rad")
    print()
    
    # 시각화
    print("4. 시각화 생성 중...")
    trajectory = np.array(trajectory)
    phases_x = np.array(phases_x)
    phases_y = np.array(phases_y)
    velocities_x = np.array(velocities_x)
    velocities_y = np.array(velocities_y)
    times = np.array(times)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. X-Y 궤적
    ax1 = axes[0, 0]
    ax1.plot(trajectory[:, 0], trajectory[:, 1], 'b-', linewidth=2, label='Trajectory')
    ax1.plot(trajectory[0, 0], trajectory[0, 1], 'go', markersize=10, label='Start')
    ax1.plot(trajectory[-1, 0], trajectory[-1, 1], 'ro', markersize=10, label='End')
    ax1.set_xlabel('X Position [m]')
    ax1.set_ylabel('Y Position [m]')
    ax1.set_title('2D Trajectory (World Coordinates)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.axis('equal')
    
    # 2. 위상 변화 (X, Y)
    ax2 = axes[0, 1]
    ax2.plot(times, phases_x, 'r-', linewidth=2, label='Phase X')
    ax2.plot(times, phases_y, 'b-', linewidth=2, label='Phase Y')
    ax2.set_xlabel('Time [ms]')
    ax2.set_ylabel('Phase [rad]')
    ax2.set_title('Phase Evolution (Internal State)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. 속도 변화
    ax3 = axes[1, 0]
    ax3.plot(times, velocities_x, 'r-', linewidth=2, label='Velocity X')
    ax3.plot(times, velocities_y, 'b-', linewidth=2, label='Velocity Y')
    ax3.set_xlabel('Time [ms]')
    ax3.set_ylabel('Velocity [m/s]')
    ax3.set_title('Velocity Evolution')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. 위상 공간 (Phase Space)
    ax4 = axes[1, 1]
    ax4.plot(phases_x, phases_y, 'g-', linewidth=2, alpha=0.7)
    ax4.plot(phases_x[0], phases_y[0], 'go', markersize=10, label='Start')
    ax4.plot(phases_x[-1], phases_y[-1], 'ro', markersize=10, label='End')
    ax4.set_xlabel('Phase X [rad]')
    ax4.set_ylabel('Phase Y [rad]')
    ax4.set_title('Phase Space Trajectory')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    
    # 저장
    output_path = os.path.join(os.path.dirname(__file__), 'grid_engine_trajectory.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"   그래프 저장: {output_path}")
    print()
    
    # 최종 상태
    final_state = engine.get_state()
    final_x, final_y = phase_to_world_coordinate(final_state.phi_x, final_state.phi_y, config)
    print("5. 최종 상태:")
    print(f"   내부 위상: ({final_state.phi_x:.3f}, {final_state.phi_y:.3f}) rad")
    print(f"   관측 좌표: ({final_x:.3f}, {final_y:.3f}) m")
    print(f"   속도: ({final_state.v_x:.3f}, {final_state.v_y:.3f}) m/s")
    print()
    
    print("=" * 60)
    print("데모 완료!")
    print("=" * 60)
    print()
    print("📌 핵심 메시지:")
    print("   Grid Engine은 내부 위상 상태만 유지합니다.")
    print("   좌표 투영은 상위 시스템(이 데모)의 책임입니다.")
    print("   이는 '제어 엔진'으로서의 올바른 책임 분리입니다.")


if __name__ == "__main__":
    main()


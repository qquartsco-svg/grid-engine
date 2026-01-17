#!/usr/bin/env python3
"""
Grid 3D Engine 시각화 데모

이 데모는 Grid 3D Engine의 3D 궤적을 시각화합니다.

시각화 내용:
    1. 3D 궤적 (X-Y-Z 공간)
    2. 시간에 따른 위상 변화 (3D)
    3. 시간에 따른 속도 변화 (3D)
    4. 위상 공간 궤적 (T³ 투영)

주의:
    - matplotlib의 mplot3d 필요
    - 실행 후 `examples/grid_3d_engine_trajectory.png` 생성

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
License: MIT License
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from grid_engine.grid_3d_engine import Grid3DEngine
from grid_engine.types_3d import Grid3DInput
from grid_engine.config_3d import Grid3DConfig


def main():
    """Grid 3D Engine 시각화 데모"""
    print("=" * 60)
    print("Grid 3D Engine - 시각화 데모")
    print("=" * 60)
    print()
    
    # Grid 3D Engine 초기화 (더 큰 스케일로 설정)
    config = Grid3DConfig(
        spatial_scale_x=10.0,  # 10m 도메인
        spatial_scale_y=10.0,
        spatial_scale_z=10.0,
        dt_ms=1.0,  # 1ms 스텝 (안정 조건 만족)
        max_dt_ratio=0.2  # dt_ms < tau_ms * max_dt_ratio = 10.0 * 0.2 = 2.0
    )
    engine = Grid3DEngine(config=config, initial_x=0.0, initial_y=0.0, initial_z=0.0)
    
    # 궤적 데이터 저장
    trajectory_x = []
    trajectory_y = []
    trajectory_z = []
    phase_x = []
    phase_y = []
    phase_z = []
    velocity_x = []
    velocity_y = []
    velocity_z = []
    time_ms = []
    
    # 나선형(Helix) 궤적 생성
    print("나선형(Helix) 궤적 생성 중...")
    n_steps = 200
    
    for i in range(n_steps):
        # 나선형 운동: 원형 운동 + Z 방향 이동
        t = i * config.dt_ms / 1000.0  # [s]
        omega = 1.0  # 각속도 [rad/s]
        radius = 2.0  # 반지름 [m]
        
        # 속도 계산 (나선형)
        v_x = -radius * omega * np.sin(omega * t)
        v_y = radius * omega * np.cos(omega * t)
        v_z = 0.5  # Z 방향 일정 속도
        
        # 가속도 계산 (원형 운동)
        a_x = -radius * (omega ** 2) * np.cos(omega * t)
        a_y = -radius * (omega ** 2) * np.sin(omega * t)
        a_z = 0.0
        
        inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z, a_x=a_x, a_y=a_y, a_z=a_z)
        output = engine.step(inp)
        state = engine.get_state()
        
        # 데이터 저장
        trajectory_x.append(state.x)
        trajectory_y.append(state.y)
        trajectory_z.append(state.z)
        phase_x.append(state.phi_x)
        phase_y.append(state.phi_y)
        phase_z.append(state.phi_z)
        velocity_x.append(state.v_x)
        velocity_y.append(state.v_y)
        velocity_z.append(state.v_z)
        time_ms.append(state.t_ms)
    
    print(f"총 {n_steps} 스텝 완료")
    print()
    
    # 시각화
    print("시각화 생성 중...")
    fig = plt.figure(figsize=(16, 12))
    
    # 1. 3D 궤적
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.plot(trajectory_x, trajectory_y, trajectory_z, 'b-', linewidth=2, label='3D Trajectory')
    ax1.scatter(trajectory_x[0], trajectory_y[0], trajectory_z[0], 
                color='green', s=100, marker='o', label='Start')
    ax1.scatter(trajectory_x[-1], trajectory_y[-1], trajectory_z[-1], 
                color='red', s=100, marker='s', label='End')
    ax1.set_xlabel('X [m]')
    ax1.set_ylabel('Y [m]')
    ax1.set_zlabel('Z [m]')
    ax1.set_title('3D Trajectory (Helix Motion)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. 시간에 따른 위상 변화
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(time_ms, phase_x, 'r-', label='φx', linewidth=2)
    ax2.plot(time_ms, phase_y, 'g-', label='φy', linewidth=2)
    ax2.plot(time_ms, phase_z, 'b-', label='φz', linewidth=2)
    ax2.set_xlabel('Time [ms]')
    ax2.set_ylabel('Phase [rad]')
    ax2.set_title('Phase vs Time (3D)')
    ax2.legend()
    ax2.grid(True)
    
    # 3. 시간에 따른 속도 변화
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(time_ms, velocity_x, 'r-', label='vx', linewidth=2)
    ax3.plot(time_ms, velocity_y, 'g-', label='vy', linewidth=2)
    ax3.plot(time_ms, velocity_z, 'b-', label='vz', linewidth=2)
    ax3.set_xlabel('Time [ms]')
    ax3.set_ylabel('Velocity [m/s]')
    ax3.set_title('Velocity vs Time (3D)')
    ax3.legend()
    ax3.grid(True)
    
    # 4. 위상 공간 궤적 (T³ 투영)
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    ax4.plot(phase_x, phase_y, phase_z, 'purple', linewidth=2, label='Phase Space Trajectory')
    ax4.scatter(phase_x[0], phase_y[0], phase_z[0], 
                color='green', s=100, marker='o', label='Start')
    ax4.scatter(phase_x[-1], phase_y[-1], phase_z[-1], 
                color='red', s=100, marker='s', label='End')
    ax4.set_xlabel('Phase X [rad]')
    ax4.set_ylabel('Phase Y [rad]')
    ax4.set_zlabel('Phase Z [rad]')
    ax4.set_title('Phase Space Trajectory (T^3 = S^1 x S^1 x S^1)')
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    
    # 저장
    output_path = os.path.join(os.path.dirname(__file__), 'grid_3d_engine_trajectory.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ 시각화 저장 완료: {output_path}")
    print()
    
    # 통계 출력
    print("=" * 60)
    print("궤적 통계")
    print("=" * 60)
    print(f"총 스텝: {n_steps}")
    print(f"총 시간: {time_ms[-1]:.1f} ms")
    print(f"최종 위치: ({trajectory_x[-1]:.3f}, {trajectory_y[-1]:.3f}, {trajectory_z[-1]:.3f}) m")
    print(f"최종 위상: ({phase_x[-1]:.6f}, {phase_y[-1]:.6f}, {phase_z[-1]:.6f}) rad")
    print(f"최종 속도: ({velocity_x[-1]:.3f}, {velocity_y[-1]:.3f}, {velocity_z[-1]:.3f}) m/s")
    print()
    
    print("=" * 60)
    print("데모 완료")
    print("=" * 60)
    print()
    print("💡 시각화 파일을 확인하세요:")
    print(f"   {output_path}")


if __name__ == "__main__":
    main()


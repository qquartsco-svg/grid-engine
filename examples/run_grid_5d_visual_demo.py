#!/usr/bin/env python3
"""
Grid Engine 5D 시각화 데모
5D 궤적 및 위상 변화 시각화 (5축 CNC)

5D 확장 (5축 CNC):
    - 2D: (x, y) 궤적
    - 3D: (x, y, z) 궤적
    - 4D: (x, y, z, w) 궤적
    - 5D: (x, y, z, θa, θb) 궤적 ✨ NEW

5축 CNC 매핑:
    - 위치: (x, y, z) [m]
    - 회전: (θa, θb) [deg]

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput, Grid5DConfig


def main():
    """Grid Engine 5D 시각화 데모 (5축 CNC)"""
    print("=" * 60)
    print("Grid Engine 5D 시각화 데모 (5축 CNC)")
    print("=" * 60)
    print()
    
    # Grid 5D Engine 초기화 (더 큰 dt_ms로 시각화 개선)
    config = Grid5DConfig(dt_ms=1.0, tau_ms=10.0, max_dt_ratio=0.2)
    engine = Grid5DEngine(
        config=config,
        initial_x=0.0, initial_y=0.0, initial_z=0.0,
        initial_theta_a=0.0, initial_theta_b=0.0
    )
    
    # 궤적 데이터 저장
    trajectory = []
    phases = []
    velocities = []
    angles = []  # 회전 각도 ✨ NEW
    times = []
    
    # 등속 운동 (5D)
    print("Generating 5D trajectory (5-axis CNC)...")
    inp = Grid5DInput(
        v_x=1.0, v_y=0.5, v_z=0.3,  # 위치 속도 [m/s]
        v_a=0.5, v_b=0.3  # 회전 각속도 [deg/s] ✨ NEW
    )
    
    n_steps = 200
    for i in range(n_steps):
        output = engine.step(inp)
        state = engine.get_state()
        
        # 좌표/각도 투영 (projector 사용)
        x, y, z, theta_a, theta_b = engine.projector.phase_to_coordinate(
            state.phi_x, state.phi_y, state.phi_z, state.phi_a, state.phi_b
        )
        
        trajectory.append([x, y, z])
        phases.append([state.phi_x, state.phi_y, state.phi_z, state.phi_a, state.phi_b])
        velocities.append([state.v_x, state.v_y, state.v_z, state.v_a, state.v_b])
        angles.append([theta_a, theta_b])  # 회전 각도 ✨ NEW
        times.append(state.t_ms / 1000.0)  # ms → s
    
    trajectory = np.array(trajectory)
    phases = np.array(phases)
    velocities = np.array(velocities)
    angles = np.array(angles)  # 회전 각도 ✨ NEW
    times = np.array(times)
    
    print(f"Trajectory generated: {n_steps} steps")
    print(f"Final position: ({trajectory[-1, 0]:.3f}, {trajectory[-1, 1]:.3f}, {trajectory[-1, 2]:.3f}) m")
    print(f"Final angles: A={angles[-1, 0]:.2f}°, B={angles[-1, 1]:.2f}°")
    print()
    
    # 시각화
    print("Creating visualizations...")
    
    # 1. 3D 궤적 (X, Y, Z만 표시, A는 색상으로, B는 크기로)
    fig = plt.figure(figsize=(16, 12))
    
    # 1-1. 3D 궤적 (X, Y, Z, A 색상, B 크기)
    ax1 = fig.add_subplot(2, 3, 1, projection='3d')
    scatter = ax1.scatter(
        trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
        c=angles[:, 0],  # A축 각도를 색상으로
        s=angles[:, 1] * 10 + 10,  # B축 각도를 크기로
        cmap='viridis', alpha=0.6
    )
    ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 'b-', alpha=0.3, linewidth=1)
    ax1.set_xlabel('X [m]')
    ax1.set_ylabel('Y [m]')
    ax1.set_zlabel('Z [m]')
    ax1.set_title('5D Trajectory (X, Y, Z; A as color, B as size)')
    plt.colorbar(scatter, ax=ax1, label='A angle [deg]')
    
    # 1-2. 위상 변화 (5D)
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(times, phases[:, 0], 'r-', label='φx (position)', linewidth=1.5)
    ax2.plot(times, phases[:, 1], 'g-', label='φy (position)', linewidth=1.5)
    ax2.plot(times, phases[:, 2], 'b-', label='φz (position)', linewidth=1.5)
    ax2.plot(times, phases[:, 3], 'm-', label='φa (rotation)', linewidth=1.5)
    ax2.plot(times, phases[:, 4], 'c-', label='φb (rotation)', linewidth=1.5)
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Phase [rad]')
    ax2.set_title('Phase Changes (5D: 3 position + 2 rotation)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 1-3. 속도 변화 (5D)
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.plot(times, velocities[:, 0], 'r-', label='vx (position)', linewidth=1.5)
    ax3.plot(times, velocities[:, 1], 'g-', label='vy (position)', linewidth=1.5)
    ax3.plot(times, velocities[:, 2], 'b-', label='vz (position)', linewidth=1.5)
    ax3.plot(times, velocities[:, 3], 'm-', label='va (rotation)', linewidth=1.5)
    ax3.plot(times, velocities[:, 4], 'c-', label='vb (rotation)', linewidth=1.5)
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Velocity [m/s] or [deg/s]')
    ax3.set_title('Velocity Changes (5D: 3 position + 2 rotation)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 1-4. 회전 각도 변화 (A, B)
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.plot(times, angles[:, 0], 'm-', label='θa (A-axis)', linewidth=1.5)
    ax4.plot(times, angles[:, 1], 'c-', label='θb (B-axis)', linewidth=1.5)
    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel('Angle [deg]')
    ax4.set_title('Rotation Angles (A, B axes)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 1-5. 위상 공간 궤적 (2D 투영: 위치 X-Y, 회전 A-B)
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.plot(phases[:, 0], phases[:, 1], 'r-', alpha=0.6, linewidth=1, label='(φx, φy) position')
    ax5.plot(phases[:, 3], phases[:, 4], 'm-', alpha=0.6, linewidth=1, label='(φa, φb) rotation')
    ax5.set_xlabel('Phase [rad]')
    ax5.set_ylabel('Phase [rad]')
    ax5.set_title('Phase Space Trajectory (2D projections)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 1-6. 위치 vs 회전 (3D 위치와 회전 각도의 관계)
    ax6 = fig.add_subplot(2, 3, 6, projection='3d')
    ax6.scatter(
        trajectory[:, 0], trajectory[:, 1], angles[:, 0],
        c=angles[:, 1], cmap='coolwarm', s=20, alpha=0.6
    )
    ax6.set_xlabel('X [m]')
    ax6.set_ylabel('Y [m]')
    ax6.set_zlabel('A angle [deg]')
    ax6.set_title('Position vs Rotation (X, Y, A; B as color)')
    
    plt.tight_layout()
    
    # 저장
    output_path = os.path.join(os.path.dirname(__file__), 'grid_engine_5d_trajectory.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved: {output_path}")
    print()
    
    plt.show()
    
    print("=" * 60)
    print("5D 시각화 데모 완료! (5축 CNC 시뮬레이션)")
    print("=" * 60)


if __name__ == "__main__":
    main()


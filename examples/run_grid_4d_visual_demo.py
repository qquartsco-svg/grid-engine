#!/usr/bin/env python3
"""
Grid Engine 4D 시각화 데모
4D 궤적 및 위상 변화 시각화

4D 확장:
    - 2D: (x, y) 궤적
    - 3D: (x, y, z) 궤적
    - 4D: (x, y, z, w) 궤적 ✨ NEW

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim4d import Grid4DEngine, Grid4DInput, Grid4DConfig


def main():
    """Grid Engine 4D 시각화 데모"""
    print("=" * 60)
    print("Grid Engine 4D 시각화 데모")
    print("=" * 60)
    print()
    
    # Grid 4D Engine 초기화 (더 큰 dt_ms로 시각화 개선)
    config = Grid4DConfig(dt_ms=1.0, tau_ms=10.0, max_dt_ratio=0.2)
    engine = Grid4DEngine(config=config, initial_x=0.0, initial_y=0.0, initial_z=0.0, initial_w=0.0)
    
    # 궤적 데이터 저장
    trajectory = []
    phases = []
    velocities = []
    times = []
    
    # 등속 운동 (4D)
    print("Generating 4D trajectory...")
    inp = Grid4DInput(v_x=1.0, v_y=0.5, v_z=0.3, v_w=0.2)
    
    n_steps = 200
    for i in range(n_steps):
        output = engine.step(inp)
        state = engine.get_state()
        
        # 좌표 투영 (projector 사용)
        x, y, z, w = engine.projector.phase_to_coordinate(
            state.phi_x, state.phi_y, state.phi_z, state.phi_w
        )
        
        trajectory.append([x, y, z, w])
        phases.append([state.phi_x, state.phi_y, state.phi_z, state.phi_w])
        velocities.append([state.v_x, state.v_y, state.v_z, state.v_w])
        times.append(state.t_ms / 1000.0)  # ms → s
    
    trajectory = np.array(trajectory)
    phases = np.array(phases)
    velocities = np.array(velocities)
    times = np.array(times)
    
    print(f"Trajectory generated: {n_steps} steps")
    print(f"Final position: ({trajectory[-1, 0]:.3f}, {trajectory[-1, 1]:.3f}, {trajectory[-1, 2]:.3f}, {trajectory[-1, 3]:.3f}) m")
    print()
    
    # 시각화
    print("Creating visualizations...")
    
    # 1. 3D 궤적 (X, Y, Z만 표시, W는 색상으로)
    fig = plt.figure(figsize=(16, 12))
    
    # 1-1. 3D 궤적 (X, Y, Z, W 색상)
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    scatter = ax1.scatter(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 
                         c=trajectory[:, 3], cmap='viridis', s=10, alpha=0.6)
    ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 'b-', alpha=0.3, linewidth=1)
    ax1.set_xlabel('X [m]')
    ax1.set_ylabel('Y [m]')
    ax1.set_zlabel('Z [m]')
    ax1.set_title('4D Trajectory (X, Y, Z; W as color)')
    plt.colorbar(scatter, ax=ax1, label='W [m]')
    
    # 1-2. 위상 변화 (4D)
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(times, phases[:, 0], 'r-', label='φx', linewidth=1.5)
    ax2.plot(times, phases[:, 1], 'g-', label='φy', linewidth=1.5)
    ax2.plot(times, phases[:, 2], 'b-', label='φz', linewidth=1.5)
    ax2.plot(times, phases[:, 3], 'm-', label='φw', linewidth=1.5)
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Phase [rad]')
    ax2.set_title('Phase Changes (4D)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 1-3. 속도 변화 (4D)
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(times, velocities[:, 0], 'r-', label='vx', linewidth=1.5)
    ax3.plot(times, velocities[:, 1], 'g-', label='vy', linewidth=1.5)
    ax3.plot(times, velocities[:, 2], 'b-', label='vz', linewidth=1.5)
    ax3.plot(times, velocities[:, 3], 'm-', label='vw', linewidth=1.5)
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Velocity [m/s]')
    ax3.set_title('Velocity Changes (4D)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 1-4. 위상 공간 궤적 (2D 투영: X-Y, Z-W)
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(phases[:, 0], phases[:, 1], 'r-', alpha=0.6, linewidth=1, label='(φx, φy)')
    ax4.plot(phases[:, 2], phases[:, 3], 'b-', alpha=0.6, linewidth=1, label='(φz, φw)')
    ax4.set_xlabel('Phase [rad]')
    ax4.set_ylabel('Phase [rad]')
    ax4.set_title('Phase Space Trajectory (2D projections)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 저장
    output_path = os.path.join(os.path.dirname(__file__), 'grid_engine_4d_trajectory.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved: {output_path}")
    print()
    
    plt.show()
    
    print("=" * 60)
    print("4D 시각화 데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()


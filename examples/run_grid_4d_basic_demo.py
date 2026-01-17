#!/usr/bin/env python3
"""
Grid Engine 4D 기본 데모
4D 위치 상태 유지 및 경로 통합 시연

4D 확장:
    - 2D: (x, y), (φx, φy)
    - 3D: (x, y, z), (φx, φy, φz)
    - 4D: (x, y, z, w), (φx, φy, φz, φw) ✨ NEW

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.3.0-alpha (4D extension)
License: MIT License
"""

import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim4d import Grid4DEngine, Grid4DInput, Grid4DConfig


def main():
    """Grid Engine 4D 기본 데모"""
    print("=" * 60)
    print("Grid Engine 4D 기본 데모")
    print("=" * 60)
    print()
    print("📌 참고: Grid 4D Engine은 내부 위상 상태만 유지합니다.")
    print("   좌표 투영은 상위 시스템의 책임입니다.")
    print("   시각화 데모: examples/run_grid_4d_visual_demo.py")
    print()
    
    # Grid 4D Engine 초기화
    print("1. Grid 4D Engine 초기화...")
    engine = Grid4DEngine(initial_x=0.0, initial_y=0.0, initial_z=0.0, initial_w=0.0)
    state = engine.get_state()
    print(f"   초기 위상 (내부 상태): ({state.phi_x:.3f}, {state.phi_y:.3f}, {state.phi_z:.3f}, {state.phi_w:.3f}) rad")
    print(f"   초기 속도: ({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}, {state.v_w:.2f}) m/s")
    print()
    
    # 일정한 속도로 이동 (4D)
    print("2. 일정한 속도로 이동 (v_x=1.0, v_y=0.5, v_z=0.3, v_w=0.2)...")
    inp = Grid4DInput(v_x=1.0, v_y=0.5, v_z=0.3, v_w=0.2)
    
    for i in range(10):
        output = engine.step(inp)
        state = engine.get_state()
        if (i + 1) % 2 == 1:  # 홀수 스텝만 출력
            print(f"   Step {i+1}: 위상=({state.phi_x:.3f}, {state.phi_y:.3f}, {state.phi_z:.3f}, {state.phi_w:.3f}) rad, "
                  f"속도=({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}, {state.v_w:.2f}) m/s")
    print()
    
    # 가속도를 포함한 이동 (4D)
    print("3. 가속도를 포함한 이동 (a_x=0.1, a_y=0.05, a_z=0.03, a_w=0.02)...")
    inp = Grid4DInput(v_x=1.0, v_y=0.5, v_z=0.3, v_w=0.2, a_x=0.1, a_y=0.05, a_z=0.03, a_w=0.02)
    
    for i in range(10):
        output = engine.step(inp)
        state = engine.get_state()
        if (i + 1) % 2 == 1:  # 홀수 스텝만 출력
            print(f"   Step {i+1}: 위상=({state.phi_x:.3f}, {state.phi_y:.3f}, {state.phi_z:.3f}, {state.phi_w:.3f}) rad, "
                  f"속도=({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}, {state.v_w:.2f}) m/s")
    print()
    
    # 최종 상태
    print("4. 최종 상태:")
    state = engine.get_state()
    print(f"   내부 위상: ({state.phi_x:.6f}, {state.phi_y:.6f}, {state.phi_z:.6f}, {state.phi_w:.6f}) rad")
    print(f"   속도: ({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}, {state.v_w:.2f}) m/s")
    print()
    
    print("💡 좌표 투영이 필요하면:")
    print("   python examples/run_grid_4d_visual_demo.py")
    print()
    print("=" * 60)
    print("4D 데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()


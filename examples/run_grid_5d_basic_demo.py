#!/usr/bin/env python3
"""
Grid Engine 5D 기본 데모
5D 위치/각도 상태 유지 및 경로 통합 시연 (5축 CNC)

5D 확장 (5축 CNC):
    - 2D: (x, y), (φx, φy)
    - 3D: (x, y, z), (φx, φy, φz)
    - 4D: (x, y, z, w), (φx, φy, φz, φw)
    - 5D: (x, y, z, θa, θb), (φx, φy, φz, φa, φb) ✨ NEW

5축 CNC 매핑:
    - 위치 축 (3개): X, Y, Z (선형 이동) [m]
    - 회전 축 (2개): A, B (각도 회전) [deg]

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput, Grid5DConfig


def main():
    """Grid Engine 5D 기본 데모 (5축 CNC)"""
    print("=" * 60)
    print("Grid Engine 5D 기본 데모 (5축 CNC)")
    print("=" * 60)
    print()
    print("📌 참고: Grid 5D Engine은 내부 위상 상태만 유지합니다.")
    print("   좌표/각도 투영은 상위 시스템의 책임입니다.")
    print("   시각화 데모: examples/run_grid_5d_visual_demo.py")
    print()
    print("5축 CNC 매핑:")
    print("   - 위치 축 (3개): X, Y, Z [m]")
    print("   - 회전 축 (2개): A, B [deg]")
    print()
    
    # Grid 5D Engine 초기화
    print("1. Grid 5D Engine 초기화...")
    engine = Grid5DEngine(
        initial_x=0.0, initial_y=0.0, initial_z=0.0,
        initial_theta_a=0.0, initial_theta_b=0.0
    )
    state = engine.get_state()
    print(f"   초기 위상 (내부 상태): ({state.phi_x:.3f}, {state.phi_y:.3f}, {state.phi_z:.3f}, {state.phi_a:.3f}, {state.phi_b:.3f}) rad")
    print(f"   초기 위치: ({state.x:.3f}, {state.y:.3f}, {state.z:.3f}) m")
    print(f"   초기 각도: A={state.theta_a:.2f}°, B={state.theta_b:.2f}°")
    print(f"   초기 속도: 위치=({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}) m/s, 회전=({state.v_a:.2f}, {state.v_b:.2f}) deg/s")
    print()
    
    # 일정한 속도로 이동 (5D)
    print("2. 일정한 속도로 이동 (5축 CNC)...")
    print("   위치: v_x=1.0, v_y=0.5, v_z=0.3 m/s")
    print("   회전: v_a=0.5, v_b=0.3 deg/s (입력) → 내부 변환 rad/s")
    inp = Grid5DInput(
        v_x=1.0, v_y=0.5, v_z=0.3,  # 위치 속도 [m/s]
        v_a=0.5, v_b=0.3  # 회전 각속도 [deg/s] (입력 단위) → integrator에서 rad/s로 변환 ✨ NEW
    )
    
    for i in range(10):
        output = engine.step(inp)
        state = engine.get_state()
        if (i + 1) % 2 == 1:  # 홀수 스텝만 출력
            print(f"   Step {i+1}: 위치=({state.x:.3f}, {state.y:.3f}, {state.z:.3f}) m, "
                  f"각도=(A={state.theta_a:.2f}°, B={state.theta_b:.2f}°), "
                  f"위상=({state.phi_x:.3f}, {state.phi_y:.3f}, {state.phi_z:.3f}, {state.phi_a:.3f}, {state.phi_b:.3f}) rad")
    print()
    
    # 가속도를 포함한 이동 (5D)
    print("3. 가속도를 포함한 이동 (5축 CNC)...")
    print("   위치: a_x=0.1, a_y=0.05, a_z=0.03 m/s²")
    print("   회전: alpha_a=0.05, alpha_b=0.03 deg/s² (입력) → 내부 변환 rad/s²")
    inp = Grid5DInput(
        v_x=1.0, v_y=0.5, v_z=0.3,  # 위치 속도 [m/s]
        v_a=0.5, v_b=0.3,  # 회전 각속도 [deg/s] (입력 단위)
        a_x=0.1, a_y=0.05, a_z=0.03,  # 위치 가속도 [m/s²]
        alpha_a=0.05, alpha_b=0.03  # 회전 각가속도 [deg/s²] (입력 단위) → integrator에서 rad/s²로 변환 ✨ NEW
    )
    
    for i in range(10):
        output = engine.step(inp)
        state = engine.get_state()
        if (i + 1) % 2 == 1:  # 홀수 스텝만 출력
            print(f"   Step {i+1}: 위치=({state.x:.3f}, {state.y:.3f}, {state.z:.3f}) m, "
                  f"각도=(A={state.theta_a:.2f}°, B={state.theta_b:.2f}°), "
                  f"속도=위치({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}) m/s, 회전({state.v_a:.2f}, {state.v_b:.2f}) deg/s")
    print()
    
    # 최종 상태
    print("4. 최종 상태:")
    state = engine.get_state()
    print(f"   내부 위상: ({state.phi_x:.6f}, {state.phi_y:.6f}, {state.phi_z:.6f}, {state.phi_a:.6f}, {state.phi_b:.6f}) rad")
    print(f"   위치: ({state.x:.6f}, {state.y:.6f}, {state.z:.6f}) m")
    print(f"   각도: A={state.theta_a:.2f}°, B={state.theta_b:.2f}°")
    print(f"   속도: 위치=({state.v_x:.2f}, {state.v_y:.2f}, {state.v_z:.2f}) m/s, 회전=({state.v_a:.2f}, {state.v_b:.2f}) deg/s")
    print()
    
    print("💡 좌표/각도 투영이 필요하면:")
    print("   python examples/run_grid_5d_visual_demo.py")
    print()
    print("=" * 60)
    print("5D 데모 완료! (5축 CNC 시뮬레이션)")
    print("=" * 60)


if __name__ == "__main__":
    main()


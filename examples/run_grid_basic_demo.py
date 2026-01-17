#!/usr/bin/env python3
"""
Grid Engine 기본 데모
2D 위치 상태 유지 및 경로 통합 시연
"""

import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine import GridEngine, GridInput, GridEngineConfig


def main():
    """Grid Engine 기본 데모"""
    print("=" * 60)
    print("Grid Engine 기본 데모")
    print("=" * 60)
    print()
    print("📌 참고: Grid Engine은 내부 위상 상태만 유지합니다.")
    print("   좌표 투영은 상위 시스템의 책임입니다.")
    print("   시각화 데모: examples/run_grid_visual_demo.py")
    print()
    
    # Grid Engine 초기화
    print("1. Grid Engine 초기화...")
    engine = GridEngine(initial_x=0.0, initial_y=0.0)
    state = engine.get_state()
    print(f"   초기 위상 (내부 상태): ({state.phi_x:.3f}, {state.phi_y:.3f}) rad")
    print(f"   초기 속도: ({state.v_x:.2f}, {state.v_y:.2f}) m/s")
    print()
    
    # 일정한 속도로 이동
    print("2. 일정한 속도로 이동 (v_x=1.0, v_y=0.0)...")
    inp = GridInput(v_x=1.0, v_y=0.0)
    
    for i in range(10):
        output = engine.step(inp)
        if i % 2 == 0:
            state = engine.get_state()
            print(f"   Step {i+1}: 위상=({output.phi_x:.3f}, {output.phi_y:.3f}) rad, "
                  f"속도=({state.v_x:.2f}, {state.v_y:.2f}) m/s")
    print()
    
    # 가속도를 포함한 이동
    print("3. 가속도를 포함한 이동 (a_x=0.1, a_y=0.0)...")
    inp_accel = GridInput(v_x=0.0, v_y=0.0, a_x=0.1, a_y=0.0)
    
    for i in range(10):
        output = engine.step(inp_accel)
        if i % 2 == 0:
            state = engine.get_state()
            print(f"   Step {i+1}: 위상=({output.phi_x:.3f}, {output.phi_y:.3f}) rad, "
                  f"속도=({state.v_x:.2f}, {state.v_y:.2f}) m/s")
    print()
    
    # 최종 상태
    final_state = engine.get_state()
    print("4. 최종 상태:")
    print(f"   내부 위상: ({final_state.phi_x:.3f}, {final_state.phi_y:.3f}) rad")
    print(f"   속도: ({final_state.v_x:.2f}, {final_state.v_y:.2f}) m/s")
    print()
    print("💡 좌표 투영이 필요하면:")
    print("   python examples/run_grid_visual_demo.py")
    print()
    
    print("=" * 60)
    print("데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()


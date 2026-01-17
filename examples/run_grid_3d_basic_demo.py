#!/usr/bin/env python3
"""
Grid 3D Engine 기본 데모

이 데모는 Grid 3D Engine의 기본 기능을 시연합니다.

데모 내용:
    1. 초기화 (3D)
    2. 등속 운동 (3D)
    3. 등가속도 운동 (3D)
    4. 상태 출력 (3D)

주의:
    - Grid 3D Engine은 내부 위상(φx, φy, φz)만 관리합니다.
    - 좌표 투영은 상위 시스템(이 데모)의 책임입니다.

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
License: MIT License
"""

import sys
import os

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from grid_engine.grid_3d_engine import Grid3DEngine
from grid_engine.types_3d import Grid3DInput


def main():
    """Grid 3D Engine 기본 데모"""
    print("=" * 60)
    print("Grid 3D Engine - 기본 데모")
    print("=" * 60)
    print()
    
    # 1. 초기화 (3D)
    print("[1] 초기화 (3D)")
    print("-" * 60)
    engine = Grid3DEngine(initial_x=0.0, initial_y=0.0, initial_z=0.0)
    state = engine.get_state()
    
    print(f"초기 상태:")
    print(f"  위상: ({state.phi_x:.6f}, {state.phi_y:.6f}, {state.phi_z:.6f}) rad")
    print(f"  좌표: ({state.x:.3f}, {state.y:.3f}, {state.z:.3f}) m")
    print(f"  속도: ({state.v_x:.3f}, {state.v_y:.3f}, {state.v_z:.3f}) m/s")
    print()
    
    # 2. 등속 운동 (3D)
    print("[2] 등속 운동 (3D)")
    print("-" * 60)
    v_x = 1.0  # m/s
    v_y = 0.5  # m/s
    v_z = 0.3  # m/s (Z 방향 추가)
    
    inp = Grid3DInput(v_x=v_x, v_y=v_y, v_z=v_z)
    
    print(f"입력 속도: ({v_x:.1f}, {v_y:.1f}, {v_z:.1f}) m/s")
    print()
    print("스텝별 상태:")
    print(f"{'스텝':<6} {'위상 X':<12} {'위상 Y':<12} {'위상 Z':<12} {'좌표 X':<12} {'좌표 Y':<12} {'좌표 Z':<12} {'속도 X':<10} {'속도 Y':<10} {'속도 Z':<10}")
    print("-" * 130)
    
    for i in range(5):
        output = engine.step(inp)
        state = engine.get_state()
        
        print(f"{i+1:<6} {state.phi_x:12.6f} {state.phi_y:12.6f} {state.phi_z:12.6f} "
              f"{state.x:12.6f} {state.y:12.6f} {state.z:12.6f} "
              f"{state.v_x:10.3f} {state.v_y:10.3f} {state.v_z:10.3f}")
    
    print()
    
    # 3. 등가속도 운동 (3D)
    print("[3] 등가속도 운동 (3D)")
    print("-" * 60)
    a_x = 0.1  # m/s²
    a_y = 0.05  # m/s²
    a_z = 0.03  # m/s² (Z 방향 추가)
    
    inp = Grid3DInput(v_x=state.v_x, v_y=state.v_y, v_z=state.v_z, 
                     a_x=a_x, a_y=a_y, a_z=a_z)
    
    print(f"입력 가속도: ({a_x:.2f}, {a_y:.2f}, {a_z:.2f}) m/s²")
    print()
    print("스텝별 상태:")
    print(f"{'스텝':<6} {'위상 X':<12} {'위상 Y':<12} {'위상 Z':<12} {'좌표 X':<12} {'좌표 Y':<12} {'좌표 Z':<12} {'속도 X':<10} {'속도 Y':<10} {'속도 Z':<10}")
    print("-" * 130)
    
    for i in range(5):
        output = engine.step(inp)
        state = engine.get_state()
        
        print(f"{i+6:<6} {state.phi_x:12.6f} {state.phi_y:12.6f} {state.phi_z:12.6f} "
              f"{state.x:12.6f} {state.y:12.6f} {state.z:12.6f} "
              f"{state.v_x:10.3f} {state.v_y:10.3f} {state.v_z:10.3f}")
    
    print()
    
    # 4. 최종 상태 (3D)
    print("[4] 최종 상태 (3D)")
    print("-" * 60)
    state = engine.get_state()
    
    print(f"최종 위상: ({state.phi_x:.6f}, {state.phi_y:.6f}, {state.phi_z:.6f}) rad")
    print(f"최종 좌표: ({state.x:.6f}, {state.y:.6f}, {state.z:.6f}) m")
    print(f"최종 속도: ({state.v_x:.3f}, {state.v_y:.3f}, {state.v_z:.3f}) m/s")
    print(f"경과 시간: {state.t_ms:.1f} ms")
    print()
    
    print("=" * 60)
    print("데모 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()


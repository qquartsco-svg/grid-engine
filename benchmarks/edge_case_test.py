"""
엣지 케이스 테스트 (Edge Case Testing)

극단적인 상황에서의 동작을 테스트합니다.

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
from typing import Dict
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DConfig


def test_zero_state():
    """영 상태 테스트"""
    print("\n" + "="*80)
    print("엣지 케이스: 영 상태 (Zero State)")
    print("="*80 + "\n")
    
    try:
        engine = Grid5DEngine(
            initial_x=0.0, initial_y=0.0, initial_z=0.0,
            initial_theta_a=0.0, initial_theta_b=0.0
        )
        engine.set_target(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
        engine.update(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
        reference = engine.provide_reference()
        print(f"✅ 영 상태 처리 성공: reference = {reference}")
        return True
    except Exception as e:
        print(f"❌ 영 상태 처리 실패: {e}")
        return False


def test_large_values():
    """큰 값 테스트"""
    print("\n" + "="*80)
    print("엣지 케이스: 큰 값 (Large Values)")
    print("="*80 + "\n")
    
    try:
        engine = Grid5DEngine(
            initial_x=100.0, initial_y=100.0, initial_z=100.0,
            initial_theta_a=360.0, initial_theta_b=360.0
        )
        engine.set_target(np.array([100.0, 100.0, 100.0, 360.0, 360.0]))
        engine.update(np.array([100.0, 100.0, 100.0, 360.0, 360.0]))
        reference = engine.provide_reference()
        print(f"✅ 큰 값 처리 성공: reference = {reference}")
        return True
    except Exception as e:
        print(f"❌ 큰 값 처리 실패: {e}")
        return False


def test_rapid_changes():
    """급격한 변화 테스트"""
    print("\n" + "="*80)
    print("엣지 케이스: 급격한 변화 (Rapid Changes)")
    print("="*80 + "\n")
    
    try:
        engine = Grid5DEngine(
            initial_x=0.0, initial_y=0.0, initial_z=0.0,
            initial_theta_a=0.0, initial_theta_b=0.0
        )
        engine.set_target(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
        
        # 급격한 변화 시뮬레이션
        for i in range(10):
            current = np.array([i * 10.0, i * 10.0, i * 10.0, i * 10.0, i * 10.0])
            engine.update(current)
        
        reference = engine.provide_reference()
        print(f"✅ 급격한 변화 처리 성공: reference = {reference}")
        return True
    except Exception as e:
        print(f"❌ 급격한 변화 처리 실패: {e}")
        return False


def test_negative_values():
    """음수 값 테스트"""
    print("\n" + "="*80)
    print("엣지 케이스: 음수 값 (Negative Values)")
    print("="*80 + "\n")
    
    try:
        engine = Grid5DEngine(
            initial_x=-10.0, initial_y=-10.0, initial_z=-10.0,
            initial_theta_a=-180.0, initial_theta_b=-180.0
        )
        engine.set_target(np.array([-10.0, -10.0, -10.0, -180.0, -180.0]))
        engine.update(np.array([-10.0, -10.0, -10.0, -180.0, -180.0]))
        reference = engine.provide_reference()
        print(f"✅ 음수 값 처리 성공: reference = {reference}")
        return True
    except Exception as e:
        print(f"❌ 음수 값 처리 실패: {e}")
        return False


def test_nan_inf():
    """NaN/Inf 테스트"""
    print("\n" + "="*80)
    print("엣지 케이스: NaN/Inf 처리")
    print("="*80 + "\n")
    
    try:
        engine = Grid5DEngine(
            initial_x=0.0, initial_y=0.0, initial_z=0.0,
            initial_theta_a=0.0, initial_theta_b=0.0
        )
        engine.set_target(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
        
        # NaN/Inf 입력 시뮬레이션
        current = np.array([np.nan, np.inf, -np.inf, 0.0, 0.0])
        engine.update(current)
        reference = engine.provide_reference()
        
        # NaN/Inf가 reference에 포함되어 있는지 확인
        if np.any(np.isnan(reference)) or np.any(np.isinf(reference)):
            print(f"⚠️ NaN/Inf가 reference에 포함됨: {reference}")
            return False
        else:
            print(f"✅ NaN/Inf 처리 성공: reference = {reference}")
            return True
    except Exception as e:
        print(f"❌ NaN/Inf 처리 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    print("="*80)
    print("엣지 케이스 테스트")
    print("="*80)
    
    results = {
        'zero_state': test_zero_state(),
        'large_values': test_large_values(),
        'rapid_changes': test_rapid_changes(),
        'negative_values': test_negative_values(),
        'nan_inf': test_nan_inf(),
    }
    
    # 종합 결과
    print("\n" + "="*80)
    print("종합 결과")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    print(f"\n통과율: {passed}/{total} ({passed/total*100:.1f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🔬 모든 엣지 케이스 테스트 통과 (초기 검증 완료)")
    else:
        print("\n⚠️ 일부 엣지 케이스 테스트 실패 - 추가 검증 필요")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()


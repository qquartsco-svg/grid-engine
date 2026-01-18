#!/usr/bin/env python3
"""
6D와 7D Grid Engine 테스트 스크립트

이 스크립트는 6D와 7D Grid Engine의 기본 동작을 테스트합니다.

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha
License: MIT License
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning, message='.*Glyph.*missing from font.*')

import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)

import numpy as np
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput
from grid_engine.dimensions.dim6d import Grid6DEngine, Grid6DInput
from grid_engine.dimensions.dim7d import Grid7DEngine, Grid7DInput


def test_basic_operation():
    """기본 동작 테스트"""
    print("=" * 70)
    print("6D와 7D Grid Engine 기본 동작 테스트")
    print("=" * 70)
    print()
    
    n_steps = 100
    
    # 5D 테스트
    print("📊 5D Grid Engine (5개 Ring: X, Y, Z, A, B)")
    try:
        engine_5d = Grid5DEngine()
        inp_5d = Grid5DInput(v_x=0.1, v_y=0.1, v_z=0.1, v_a=1.0, v_b=1.0)
        for i in range(n_steps):
            output_5d = engine_5d.step(inp_5d)
        print(f"   ✅ 성공: 최종 위치 ({output_5d.x:.4f}, {output_5d.y:.4f}, {output_5d.z:.4f}) m")
        print(f"   ✅ 성공: 최종 각도 ({output_5d.theta_a:.2f}°, {output_5d.theta_b:.2f}°)")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()
    
    # 6D 테스트
    print("📊 6D Grid Engine (6개 Ring: X, Y, Z, A, B, C)")
    try:
        engine_6d = Grid6DEngine()
        inp_6d = Grid6DInput(v_x=0.1, v_y=0.1, v_z=0.1, v_a=1.0, v_b=1.0, v_c=1.0)
        for i in range(n_steps):
            output_6d = engine_6d.step(inp_6d)
        print(f"   ✅ 성공: 최종 위치 ({output_6d.x:.4f}, {output_6d.y:.4f}, {output_6d.z:.4f}) m")
        print(f"   ✅ 성공: 최종 각도 ({output_6d.theta_a:.2f}°, {output_6d.theta_b:.2f}°, {output_6d.theta_c:.2f}°)")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()
    
    # 7D 테스트
    print("📊 7D Grid Engine (7개 Ring: X, Y, Z, A, B, C, D)")
    try:
        engine_7d = Grid7DEngine()
        inp_7d = Grid7DInput(v_x=0.1, v_y=0.1, v_z=0.1, v_a=1.0, v_b=1.0, v_c=1.0, v_d=1.0)
        for i in range(n_steps):
            output_7d = engine_7d.step(inp_7d)
        print(f"   ✅ 성공: 최종 위치 ({output_7d.x:.4f}, {output_7d.y:.4f}, {output_7d.z:.4f}) m")
        print(f"   ✅ 성공: 최종 각도 ({output_7d.theta_a:.2f}°, {output_7d.theta_b:.2f}°, {output_7d.theta_c:.2f}°, {output_7d.theta_d:.2f}°)")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()


def test_stability_comparison():
    """안정성 비교 테스트"""
    print("=" * 70)
    print("5D, 6D, 7D 안정성 비교 테스트")
    print("=" * 70)
    print()
    
    n_steps = 200
    
    # 5D 테스트
    print("📊 5D Grid Engine 안정성 테스트")
    try:
        engine_5d = Grid5DEngine()
        inp_5d = Grid5DInput(v_x=0.1, v_y=0.1, v_z=0.1, v_a=1.0, v_b=1.0)
        positions_5d = []
        for i in range(n_steps):
            output_5d = engine_5d.step(inp_5d)
            positions_5d.append([output_5d.x, output_5d.y, output_5d.z, output_5d.theta_a, output_5d.theta_b])
        positions_5d = np.array(positions_5d)
        pos_std_5d = np.mean(np.std(positions_5d[:, :3], axis=0))
        ang_std_5d = np.mean(np.std(positions_5d[:, 3:], axis=0))
        print(f"   위치 변동성 (std): {pos_std_5d:.6f}")
        print(f"   각도 변동성 (std): {ang_std_5d:.4f}°")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()
    
    # 6D 테스트
    print("📊 6D Grid Engine 안정성 테스트")
    try:
        engine_6d = Grid6DEngine()
        inp_6d = Grid6DInput(v_x=0.1, v_y=0.1, v_z=0.1, v_a=1.0, v_b=1.0, v_c=1.0)
        positions_6d = []
        for i in range(n_steps):
            output_6d = engine_6d.step(inp_6d)
            positions_6d.append([output_6d.x, output_6d.y, output_6d.z, output_6d.theta_a, output_6d.theta_b, output_6d.theta_c])
        positions_6d = np.array(positions_6d)
        pos_std_6d = np.mean(np.std(positions_6d[:, :3], axis=0))
        ang_std_6d = np.mean(np.std(positions_6d[:, 3:], axis=0))
        print(f"   위치 변동성 (std): {pos_std_6d:.6f}")
        print(f"   각도 변동성 (std): {ang_std_6d:.4f}°")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()
    
    # 7D 테스트
    print("📊 7D Grid Engine 안정성 테스트")
    try:
        engine_7d = Grid7DEngine()
        inp_7d = Grid7DInput(v_x=0.1, v_y=0.1, v_z=0.1, v_a=1.0, v_b=1.0, v_c=1.0, v_d=1.0)
        positions_7d = []
        for i in range(n_steps):
            output_7d = engine_7d.step(inp_7d)
            positions_7d.append([output_7d.x, output_7d.y, output_7d.z, output_7d.theta_a, output_7d.theta_b, output_7d.theta_c, output_7d.theta_d])
        positions_7d = np.array(positions_7d)
        pos_std_7d = np.mean(np.std(positions_7d[:, :3], axis=0))
        ang_std_7d = np.mean(np.std(positions_7d[:, 3:], axis=0))
        print(f"   위치 변동성 (std): {pos_std_7d:.6f}")
        print(f"   각도 변동성 (std): {ang_std_7d:.4f}°")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()
    
    # 비교 분석
    print("=" * 70)
    print("📈 비교 분석")
    print("=" * 70)
    try:
        print(f"5D 위치 변동성: {pos_std_5d:.6f}")
        print(f"6D 위치 변동성: {pos_std_6d:.6f}")
        print(f"7D 위치 변동성: {pos_std_7d:.6f}")
        print()
        print(f"5D 각도 변동성: {ang_std_5d:.4f}°")
        print(f"6D 각도 변동성: {ang_std_6d:.4f}°")
        print(f"7D 각도 변동성: {ang_std_7d:.4f}°")
    except:
        pass
    print()


def test_persistent_bias_estimator():
    """Persistent Bias Estimator 테스트"""
    print("=" * 70)
    print("6D/7D Persistent Bias Estimator 테스트")
    print("=" * 70)
    print()
    
    # 6D 테스트
    print("📊 6D Persistent Bias Estimator")
    try:
        engine_6d = Grid6DEngine()
        setpoint = np.array([0.5, 0.5, 0.5, 45.0, 45.0, 45.0])  # [x, y, z, theta_a, theta_b, theta_c]
        engine_6d.set_target(setpoint)
        
        # 드리프트 시뮬레이션
        drift_rate = 0.001
        for i in range(100):
            current = setpoint + drift_rate * (i + 1) + np.random.normal(0, 0.01, 6)
            engine_6d.update(current)
        
        reference = engine_6d.provide_reference()
        print(f"   ✅ Bias 추정: {reference}")
        print(f"   ✅ Bias 크기: {np.linalg.norm(reference):.6f}")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()
    
    # 7D 테스트
    print("📊 7D Persistent Bias Estimator")
    try:
        engine_7d = Grid7DEngine()
        setpoint = np.array([0.5, 0.5, 0.5, 45.0, 45.0, 45.0, 45.0])  # [x, y, z, theta_a, theta_b, theta_c, theta_d]
        engine_7d.set_target(setpoint)
        
        # 드리프트 시뮬레이션
        drift_rate = 0.001
        for i in range(100):
            current = setpoint + drift_rate * (i + 1) + np.random.normal(0, 0.01, 7)
            engine_7d.update(current)
        
        reference = engine_7d.provide_reference()
        print(f"   ✅ Bias 추정: {reference}")
        print(f"   ✅ Bias 크기: {np.linalg.norm(reference):.6f}")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
    print()


def main():
    """메인 함수"""
    print()
    print("🧪 6D와 7D Grid Engine 테스트 시작")
    print()
    
    # 기본 동작 테스트
    test_basic_operation()
    
    # 안정성 비교 테스트
    test_stability_comparison()
    
    # Persistent Bias Estimator 테스트
    test_persistent_bias_estimator()
    
    print("=" * 70)
    print("✅ 모든 테스트 완료!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()


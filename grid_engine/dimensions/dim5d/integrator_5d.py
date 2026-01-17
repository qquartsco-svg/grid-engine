"""
Semi-implicit Euler Integrator (5D)
공용 수치 적분기 (독립 모듈)

이 모듈은 5D 경로 통합(Path Integration)을 수행합니다.
뉴턴 2법칙(F = ma)을 기반으로 속도와 위치(위상)를 업데이트합니다.

⚠️ 단위 규칙 (중요):
    - 위치 축 (X, Y, Z): [m/s], [m/s²] (SI 단위)
    - 회전 축 (A, B): 입력은 [deg/s], [deg/s²] → 내부 변환 [rad/s], [rad/s²]
    - 엔진 내부: 모든 계산은 [rad], [rad/s], [rad/s²] 기준
    - deg는 오직 I/O (projector, demo 출력)에서만 사용

5D 확장 (5축 CNC):
    - 2D: semi_implicit_euler (X, Y)
    - 3D: semi_implicit_euler_3d (X, Y, Z)
    - 4D: semi_implicit_euler_4d (X, Y, Z, W)
    - 5D: semi_implicit_euler_5d (X, Y, Z, A, B) ✨ NEW

뉴턴 제2법칙과의 연관성 (5D):
    Grid 5D Engine은 뉴턴 제2법칙 (F = ma)을 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    5D 경로 통합을 통해 뉴턴 역학의 이산화된 형태를 구현합니다.
    
    물리적 대응 관계 (5D):
        위치 축 (X, Y, Z):
            물리량          Grid 5D Engine          단위
            위치 r          위상 φ (phase)           [rad]
            속도 v          속도 입력 (velocity)     [m/s]
            가속도 a        가속도 입력 (accel)      [m/s²]
            힘 F            외란 (disturbance)      [N]
        
        회전 축 (A, B):
            물리량          Grid 5D Engine          단위
            각도 θ          위상 φ (phase)           [rad]
            각속도 ω        각속도 입력 (velocity)   [deg/s] 또는 [rad/s]
            각가속도 α      각가속도 입력 (accel)    [deg/s²] 또는 [rad/s²]
            토크 τ          외란 (disturbance)      [N·m]
    
    상태 방정식 (뉴턴 역학의 이산화, 5D):
        위치 축:
            dφx/dt = vx(t)
            dφy/dt = vy(t)
            dφz/dt = vz(t)
            
            dvx/dt = ax(t)  ← 뉴턴 2법칙
            dvy/dt = ay(t)  ← 뉴턴 2법칙
            dvz/dt = az(t)  ← 뉴턴 2법칙
        
        회전 축:
            dφa/dt = va(t)
            dφb/dt = vb(t)
            
            dva/dt = αa(t)  ← 회전 운동 방정식 (τ = Iα)
            dvb/dt = αb(t)  ← 회전 운동 방정식 (τ = Iα)

물리 단위 통일:
    ⚠️ 중요: 물리 법칙 적용을 위해 ms를 s로 변환
    dt_s = dt_ms / 1000.0 [s]
    모든 물리 계산은 초(s) 단위로 수행

수치 적분 방법:
    Semi-implicit Euler 방법 사용:
        vⁿ⁺¹ = vⁿ + aⁿ·Δt
        φⁿ⁺¹ = φⁿ + vⁿ·Δt + ½aⁿ·(Δt)²
    
    이 방법은:
        - 안정성이 좋음
        - 에너지 보존 특성이 양호
        - 구현이 간단함

상세 설명:
    - docs/5D_CONCEPT_AND_EQUATIONS.md (5D 개념 및 수식)
    - docs/NEWTONS_LAW_CONNECTION.md (뉴턴 제2법칙과의 연관성)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.4.0-alpha (5D extension)
License: MIT License
"""

from typing import Tuple
import math
import numpy as np
from .types_5d import Grid5DState, Grid5DInput


def semi_implicit_euler_5d(
    state: Grid5DState,
    input_data: Grid5DInput,
    dt_ms: float,
    tau_ms: float  # 현재 미사용, 향후 확장용
) -> Tuple[float, float, float, float, float, float, float, float, float, float]:
    """
    Semi-implicit Euler 적분기 (5D)
    
    5D 경로 통합(Path Integration)을 수행합니다.
    뉴턴 2법칙(F = ma)을 기반으로 5차원 속도와 위치(위상)를 업데이트합니다.
    
    5D 확장 (5축 CNC):
        - 위치 축 (X, Y, Z): 선형 이동 [m/s, m/s²]
        - 회전 축 (A, B): 각도 회전 [deg/s, deg/s²] 또는 [rad/s, rad/s²]
    
    수식 (위치 축):
        vxⁿ⁺¹ = vxⁿ + axⁿ·Δt
        vyⁿ⁺¹ = vyⁿ + ayⁿ·Δt
        vzⁿ⁺¹ = vzⁿ + azⁿ·Δt
        
        φxⁿ⁺¹ = φxⁿ + vxⁿ·Δt + ½axⁿ·(Δt)²
        φyⁿ⁺¹ = φyⁿ + vyⁿ·Δt + ½ayⁿ·(Δt)²
        φzⁿ⁺¹ = φzⁿ + vzⁿ·Δt + ½azⁿ·(Δt)²
    
    수식 (회전 축):
        vaⁿ⁺¹ = vaⁿ + αaⁿ·Δt
        vbⁿ⁺¹ = vbⁿ + αbⁿ·Δt
        
        φaⁿ⁺¹ = φaⁿ + vaⁿ·Δt + ½αaⁿ·(Δt)²
        φbⁿ⁺¹ = φbⁿ + vbⁿ·Δt + ½αbⁿ·(Δt)²
    
    Args:
        state: 현재 5D 상태 (phi_x, phi_y, phi_z, phi_a, phi_b, v_x, v_y, v_z, v_a, v_b 포함)
        input_data: 입력 데이터 (v_x, v_y, v_z, v_a, v_b, a_x, a_y, a_z, alpha_a, alpha_b 포함)
        dt_ms: 시간 간격 [ms]
        tau_ms: 시간 상수 [ms]
    
    Returns:
        (new_phi_x, new_phi_y, new_phi_z, new_phi_a, new_phi_b,
         new_v_x, new_v_y, new_v_z, new_v_a, new_v_b)
    
    물리 단위:
        - dt_ms: [ms]
        - dt_s: [s] (dt_ms / 1000.0)
        - 위치 속도: [m/s]
        - 위치 가속도: [m/s²]
        - 회전 속도: [deg/s] 또는 [rad/s]
        - 회전 가속도: [deg/s²] 또는 [rad/s²]
        - 위상: [rad]
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # ⚠️ 중요: 물리 법칙 적용을 위해 ms를 s로 변환
    dt_s = dt_ms / 1000.0  # [s]
    
    # 위치 축 속도 업데이트 (X, Y, Z) - SI 단위 [m/s], [m/s²]
    new_v_x = state.v_x + (input_data.a_x * dt_s if input_data.a_x is not None else 0.0)
    new_v_y = state.v_y + (input_data.a_y * dt_s if input_data.a_y is not None else 0.0)
    new_v_z = state.v_z + (input_data.a_z * dt_s if input_data.a_z is not None else 0.0)
    
    # 회전 축 각속도 업데이트 (A, B)
    # ⚠️ 단위 변환: 입력 [deg/s], [deg/s²] → 내부 [rad/s], [rad/s²]
    # Rule: 엔진 내부는 무조건 rad 기준
    # 🔒 단위 계약 (Unit Contract): 입력은 deg 단위, 내부는 rad 단위
    #    이 변환은 필수이며, 실패 시 물리 법칙 위반
    #    v_a_input_rad = v_a_deg * (π / 180°)
    v_a_input_rad = math.radians(input_data.v_a)  # deg/s → rad/s (강제 변환)
    v_b_input_rad = math.radians(input_data.v_b)  # deg/s → rad/s (강제 변환)
    
    # 가속도가 없으면 입력 속도를 직접 사용 (내부 단위로 변환)
    # 가속도가 있으면 state.v_a에 가속도 적분
    # 🔒 단위 계약: alpha_a_deg → alpha_a_rad 변환 필수
    alpha_a_rad = math.radians(input_data.alpha_a) if input_data.alpha_a is not None else 0.0  # deg/s² → rad/s² (강제 변환)
    alpha_b_rad = math.radians(input_data.alpha_b) if input_data.alpha_b is not None else 0.0  # deg/s² → rad/s² (강제 변환)
    
    if input_data.alpha_a is not None:
        new_v_a = state.v_a + alpha_a_rad * dt_s  # 가속도 적분
    else:
        new_v_a = v_a_input_rad  # 입력 속도 직접 사용 (변환된 값)
    
    if input_data.alpha_b is not None:
        new_v_b = state.v_b + alpha_b_rad * dt_s  # 가속도 적분
    else:
        new_v_b = v_b_input_rad  # 입력 속도 직접 사용 (변환된 값)
    
    # 위치 축 위상 업데이트 (X, Y, Z)
    # 수식: φⁿ⁺¹ = φⁿ + vⁿ·Δt + ½aⁿ·(Δt)²
    # 단위: [rad] = [m/s] * [s] + [m/s²] * [s²] → 위상 변화량 [rad]
    dphi_x = state.v_x * dt_s + 0.5 * (input_data.a_x if input_data.a_x is not None else 0.0) * (dt_s ** 2)
    dphi_y = state.v_y * dt_s + 0.5 * (input_data.a_y if input_data.a_y is not None else 0.0) * (dt_s ** 2)
    dphi_z = state.v_z * dt_s + 0.5 * (input_data.a_z if input_data.a_z is not None else 0.0) * (dt_s ** 2)
    
    new_phi_x = state.phi_x + dphi_x
    new_phi_y = state.phi_y + dphi_y
    new_phi_z = state.phi_z + dphi_z
    
    # 회전 축 위상 업데이트 (A, B)
    # 수식: φⁿ⁺¹ = φⁿ + vⁿ·Δt + ½αⁿ·(Δt)²
    # ⚠️ 단위: [rad] = [rad/s] * [s] + [rad/s²] * [s²]
    # 주의: 위상 업데이트는 현재 state.v_a를 사용 (이미 rad/s)
    #       가속도가 있으면 추가 항 적용
    if input_data.alpha_a is not None:
        dphi_a = state.v_a * dt_s + 0.5 * alpha_a_rad * (dt_s ** 2)
    else:
        dphi_a = v_a_input_rad * dt_s  # 입력 속도 사용 (변환된 값)
    
    if input_data.alpha_b is not None:
        dphi_b = state.v_b * dt_s + 0.5 * alpha_b_rad * (dt_s ** 2)
    else:
        dphi_b = v_b_input_rad * dt_s  # 입력 속도 사용 (변환된 값)
    
    new_phi_a = state.phi_a + dphi_a
    new_phi_b = state.phi_b + dphi_b
    
    return new_phi_x, new_phi_y, new_phi_z, new_phi_a, new_phi_b, \
           new_v_x, new_v_y, new_v_z, new_v_a, new_v_b


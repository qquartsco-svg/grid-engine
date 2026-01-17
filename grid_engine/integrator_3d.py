"""
Semi-implicit Euler Integrator (3D)
3D 공용 수치 적분기 (독립 모듈)

이 모듈은 3D 경로 통합(Path Integration)을 수행합니다.
뉴턴 2법칙(F = ma)을 기반으로 3차원 속도와 위치(위상)를 업데이트합니다.

3D 확장:
    - 2D: (φx, φy), (vx, vy), (ax, ay)
    - 3D: (φx, φy, φz), (vx, vy, vz), (ax, ay, az)

뉴턴 제2법칙과의 연관성 (3D):
    Grid Engine 3D는 뉴턴 제2법칙 (F = ma)을 3차원 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    
    물리적 관계 (3D):
        F = ma → a = (ax, ay, az) = (dvx/dt, dvy/dt, dvz/dt)
        v = (vx, vy, vz) = (dx/dt, dy/dt, dz/dt)
        a = (ax, ay, az) = (d²x/dt², d²y/dt², d²z/dt²)
    
    코드 구현 (3D):
        속도 업데이트: 
          vx(t+Δt) = vx(t) + ax(t)·Δt  ← 뉴턴 2법칙
          vy(t+Δt) = vy(t) + ay(t)·Δt  ← 뉴턴 2법칙
          vz(t+Δt) = vz(t) + az(t)·Δt  ← 뉴턴 2법칙 (Z 방향 추가)
        
        위치(위상) 업데이트: 
          φx(t+Δt) = φx(t) + vx(t)·Δt + ½ax(t)·Δt²  ← 경로 통합
          φy(t+Δt) = φy(t) + vy(t)·Δt + ½ay(t)·Δt²  ← 경로 통합
          φz(t+Δt) = φz(t) + vz(t)·Δt + ½az(t)·Δt²  ← 경로 통합 (Z 방향 추가)
    
    물리 단위 통일:
        ⚠️ 중요: 물리 법칙 적용을 위해 ms를 s로 변환
        dt_s = dt_ms / 1000.0 [s]
        모든 물리 계산은 초(s) 단위로 수행

핵심 개념:
    경로 통합(Path Integration) 3D: 속도와 가속도로부터 3D 위치를 계산
    수식: r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²
    여기서 r = (x, y, z), v = (vx, vy, vz), a = (ax, ay, az)

상세 설명:
    - docs/NEWTONS_LAW_CONNECTION.md (뉴턴 2법칙)
    - docs/3D_CONCEPT_AND_EQUATIONS.md (3D 개념 및 수식)

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.2.0 (3D extension)
License: MIT License
"""

from typing import Tuple
from .types_3d import Grid3DState, Grid3DInput


def semi_implicit_euler_3d(
    state: Grid3DState,
    input_data: Grid3DInput,
    dt_ms: float,
    tau_ms: float
) -> Tuple[float, float, float, float, float, float]:
    """
    Semi-implicit Euler 적분기 (3D)
    
    3D 경로 통합(Path Integration)을 수행합니다.
    뉴턴 2법칙(F = ma)을 기반으로 3차원 속도와 위치(위상)를 업데이트합니다.
    
    수학적 배경 (3D):
        뉴턴 2법칙: F = ma → a = (ax, ay, az) = (dvx/dt, dvy/dt, dvz/dt)
        속도 적분: v(t+Δt) = v(t) + ∫a·dt
        위치 적분: r(t+Δt) = r(t) + ∫v·dt
        
        Euler 방법 (1차 근사, 3D):
            vx(t+Δt) = vx(t) + ax(t)·Δt
            vy(t+Δt) = vy(t) + ay(t)·Δt
            vz(t+Δt) = vz(t) + az(t)·Δt  ← Z 방향 추가
            
            φx(t+Δt) = φx(t) + vx(t)·Δt + ½ax(t)·Δt²
            φy(t+Δt) = φy(t) + vy(t)·Δt + ½ay(t)·Δt²
            φz(t+Δt) = φz(t) + vz(t)·Δt + ½az(t)·Δt²  ← Z 방향 추가
    
    물리 단위 통일:
        ⚠️ 중요: 물리 법칙 적용을 위해 ms를 s로 변환
        - 입력: v [m/s], a [m/s²], dt_ms [ms]
        - 변환: dt_s = dt_ms / 1000.0 [s]
        - 수식: dphi = v [m/s] * dt_s [s] + ½a [m/s²] * (dt_s [s])²
    
    알고리즘 (3D):
        1. 시간 단위 변환: dt_ms → dt_s
        2. 속도 업데이트 (3D): v_new = v_old + a * dt_s
        3. 위상 업데이트 (3D): phi_new = phi_old + v * dt_s + 0.5 * a * dt_s²
    
    Args:
        state: 현재 상태 (phi_x, phi_y, phi_z, v_x, v_y, v_z 포함)
        input_data: 입력 데이터 (3D)
            - v_x, v_y, v_z: 속도 [m/s]
            - a_x, a_y, a_z: 가속도 [m/s²] (선택적)
        dt_ms: 시간 간격 [ms]
        tau_ms: 시간 상수 [ms] (현재 미사용, 향후 확장용)
    
    Returns:
        (new_phi_x, new_phi_y, new_phi_z, new_v_x, new_v_y, new_v_z)
            - new_phi_x, new_phi_y, new_phi_z: 새로운 위상 [rad]
            - new_v_x, new_v_y, new_v_z: 새로운 속도 [m/s]
    
    Author: GNJz
    Created: 2026-01-20
    Made in GNJz
    """
    # ============================================================
    # 1. 시간 단위 변환: ms → s
    # ============================================================
    # 물리 법칙 적용을 위해 필수: SI 단위계 [s] 사용
    # dt_ms: 입력 시간 간격 [ms]
    # dt_s: 변환된 시간 간격 [s]
    dt_s = dt_ms / 1000.0  # [s]
    
    # ============================================================
    # 2. 속도 업데이트 (가속도 고려, 3D)
    # ============================================================
    # 수식: v(t+Δt) = v(t) + a·Δt
    # 단위: [m/s] = [m/s] + [m/s²] * [s]
    # 
    # 3D 확장:
    #   - 2D: vx, vy
    #   - 3D: vx, vy, vz (Z 방향 추가)
    
    # X 방향 속도
    if input_data.a_x is not None:
        # 가속도가 주어진 경우: 속도 적분
        new_v_x = state.v_x + input_data.a_x * dt_s
    else:
        # 가속도가 없는 경우: 입력 속도 직접 사용
        new_v_x = input_data.v_x
    
    # Y 방향 속도
    if input_data.a_y is not None:
        new_v_y = state.v_y + input_data.a_y * dt_s
    else:
        new_v_y = input_data.v_y
    
    # Z 방향 속도 (새로 추가)
    if input_data.a_z is not None:
        # 가속도가 주어진 경우: 속도 적분
        new_v_z = state.v_z + input_data.a_z * dt_s
    else:
        # 가속도가 없는 경우: 입력 속도 직접 사용
        new_v_z = input_data.v_z
    
    # ============================================================
    # 3. 위상 업데이트 (경로 통합, 3D)
    # ============================================================
    # 수식: phi(t+Δt) = phi(t) + v(t)·Δt + ½a(t)·Δt²
    # 
    # 물리적 의미:
    #   - v·dt: 등속 운동에 의한 위치 변화
    #   - ½a·dt²: 가속도에 의한 추가 위치 변화 (Taylor 전개 2차 항)
    #
    # 단위 분석:
    #   dphi = v [m/s] * dt [s] + 0.5 * a [m/s²] * (dt [s])²
    #        = v*dt [m] + 0.5*a*dt² [m]
    #        = (위상 변화량) [rad]
    #
    # 3D 확장:
    #   - 2D: dphi_x, dphi_y
    #   - 3D: dphi_x, dphi_y, dphi_z (Z 방향 추가)
    #
    # 주의: 위상 변화량은 직접 [rad] 단위로 계산됩니다.
    #       공간 길이를 위상으로 변환하는 스케일링은
    #       projector_3d.py의 phase_to_coordinate_3d()에서 수행됩니다.
    
    # X 방향 위상
    if input_data.a_x is not None:
        # 가속도가 주어진 경우: 2차 적분
        dphi_x = state.v_x * dt_s + 0.5 * input_data.a_x * (dt_s ** 2)
    else:
        # 가속도가 없는 경우: 1차 적분 (등속 운동)
        dphi_x = input_data.v_x * dt_s
    
    # Y 방향 위상
    if input_data.a_y is not None:
        dphi_y = state.v_y * dt_s + 0.5 * input_data.a_y * (dt_s ** 2)
    else:
        dphi_y = input_data.v_y * dt_s
    
    # Z 방향 위상 (새로 추가)
    if input_data.a_z is not None:
        # 가속도가 주어진 경우: 2차 적분
        dphi_z = state.v_z * dt_s + 0.5 * input_data.a_z * (dt_s ** 2)
    else:
        # 가속도가 없는 경우: 1차 적분 (등속 운동)
        dphi_z = input_data.v_z * dt_s
    
    # 새로운 위상 계산 (3D)
    new_phi_x = state.phi_x + dphi_x
    new_phi_y = state.phi_y + dphi_y
    new_phi_z = state.phi_z + dphi_z  # Z 방향 추가
    
    return new_phi_x, new_phi_y, new_phi_z, new_v_x, new_v_y, new_v_z


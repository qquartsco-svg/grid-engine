"""
Semi-implicit Euler Integrator
공용 수치 적분기 (독립 모듈)

이 모듈은 경로 통합(Path Integration)을 수행합니다.
뉴턴 2법칙(F = ma)을 기반으로 속도와 위치(위상)를 업데이트합니다.

뉴턴 제2법칙과의 연관성:
    Grid Engine은 뉴턴 제2법칙 (F = ma)을 위상 공간에 구현한 물리 기반 제어 엔진입니다.
    
    물리적 관계:
        F = ma → a = dv/dt (가속도는 속도의 시간 변화율)
        v = dr/dt (속도는 위치의 시간 변화율)
        a = d²r/dt² (가속도는 위치의 2차 미분)
    
    코드 구현:
        속도 업데이트: v(t+Δt) = v(t) + a(t)·Δt  ← 뉴턴 2법칙
        위치(위상) 업데이트: r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²  ← 경로 통합
    
    물리 단위 통일:
        ⚠️ 중요: 물리 법칙 적용을 위해 ms를 s로 변환
        dt_s = dt_ms / 1000.0 [s]
        모든 물리 계산은 초(s) 단위로 수행

핵심 개념:
    경로 통합(Path Integration): 속도와 가속도로부터 위치를 계산
    수식: r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²

Author: GNJz
Created: 2026-01-20
Made in GNJz
Version: v0.1.1
License: MIT License
"""

from typing import Tuple
from .types_2d import GridState, GridInput


def semi_implicit_euler(
    state: GridState,
    input_data: GridInput,
    dt_ms: float,
    tau_ms: float
) -> Tuple[float, float, float, float]:
    """
    Semi-implicit Euler 적분기
    
    경로 통합(Path Integration)을 수행합니다.
    뉴턴 2법칙(F = ma)을 기반으로 속도와 위치(위상)를 업데이트합니다.
    
    수학적 배경:
        뉴턴 2법칙: F = ma → a = dv/dt
        속도 적분: v(t+Δt) = v(t) + ∫a·dt
        위치 적분: r(t+Δt) = r(t) + ∫v·dt
        
        Euler 방법 (1차 근사):
            v(t+Δt) = v(t) + a(t)·Δt
            r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²
    
    물리 단위 통일:
        ⚠️ 중요: 물리 법칙 적용을 위해 ms를 s로 변환
        - 입력: v [m/s], a [m/s²], dt_ms [ms]
        - 변환: dt_s = dt_ms / 1000.0 [s]
        - 수식: dphi = v [m/s] * dt_s [s] + ½a [m/s²] * (dt_s [s])²
    
    알고리즘:
        1. 시간 단위 변환: dt_ms → dt_s
        2. 속도 업데이트: v_new = v_old + a * dt_s
        3. 위상 업데이트: phi_new = phi_old + v * dt_s + 0.5 * a * dt_s²
    
    Args:
        state: 현재 상태 (phi_x, phi_y, v_x, v_y 포함)
        input_data: 입력 데이터
            - v_x, v_y: 속도 [m/s]
            - a_x, a_y: 가속도 [m/s²] (선택적)
        dt_ms: 시간 간격 [ms]
        tau_ms: 시간 상수 [ms] (현재 미사용, 향후 확장용)
    
    Returns:
        (new_phi_x, new_phi_y, new_v_x, new_v_y)
            - new_phi_x, new_phi_y: 새로운 위상 [rad]
            - new_v_x, new_v_y: 새로운 속도 [m/s]
    
    Author: [작성자 시그니처]
    Created: 2026-01
    """
    # ============================================================
    # 1. 시간 단위 변환: ms → s
    # ============================================================
    # 물리 법칙 적용을 위해 필수: SI 단위계 [s] 사용
    # dt_ms: 입력 시간 간격 [ms]
    # dt_s: 변환된 시간 간격 [s]
    dt_s = dt_ms / 1000.0  # [s]
    
    # ============================================================
    # 2. 속도 업데이트 (가속도 고려)
    # ============================================================
    # 수식: v(t+Δt) = v(t) + a·Δt
    # 단위: [m/s] = [m/s] + [m/s²] * [s]
    
    if input_data.a_x is not None:
        # 가속도가 주어진 경우: 속도 적분
        new_v_x = state.v_x + input_data.a_x * dt_s
    else:
        # 가속도가 없는 경우: 입력 속도 직접 사용
        new_v_x = input_data.v_x
    
    if input_data.a_y is not None:
        new_v_y = state.v_y + input_data.a_y * dt_s
    else:
        new_v_y = input_data.v_y
    
    # ============================================================
    # 3. 위상 업데이트 (경로 통합)
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
    # 주의: 위상 변화량은 직접 [rad] 단위로 계산됩니다.
    #       공간 길이를 위상으로 변환하는 스케일링은
    #       coupling.py의 phase_to_coordinate()에서 수행됩니다.
    
    if input_data.a_x is not None:
        # 가속도가 주어진 경우: 2차 적분
        dphi_x = state.v_x * dt_s + 0.5 * input_data.a_x * (dt_s ** 2)
    else:
        # 가속도가 없는 경우: 1차 적분 (등속 운동)
        dphi_x = input_data.v_x * dt_s
    
    if input_data.a_y is not None:
        dphi_y = state.v_y * dt_s + 0.5 * input_data.a_y * (dt_s ** 2)
    else:
        dphi_y = input_data.v_y * dt_s
    
    # 새로운 위상 계산
    new_phi_x = state.phi_x + dphi_x
    new_phi_y = state.phi_y + dphi_y
    
    return new_phi_x, new_phi_y, new_v_x, new_v_y


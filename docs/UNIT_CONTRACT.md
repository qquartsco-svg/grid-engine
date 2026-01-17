# Grid Engine 단위 계약 (Unit Contract)

**단위 사용 표준 v0.4.0-alpha**

이 문서는 Grid Engine의 단위 사용 규칙을 명확히 정의합니다.

**Author: GNJz**  
**Created: 2026-01-20**  
**Made in GNJz**  
**Version: v0.4.0-alpha (5D extension)**  
**License: MIT License**

---

## 🔒 단위 계약 (Unit Contract)

Grid Engine은 물리 법칙의 일관성을 유지하기 위해 엄격한 단위 규칙을 따릅니다.

### Rule 1: 엔진 내부 (Engine Core)

**모든 내부 연산 및 상태 저장(GridState)은 라디안(rad) 단위를 사용합니다.**

```
내부 상태 (Grid5DState):
    phi_a, phi_b: [rad]        (위상)
    v_a, v_b: [rad/s]          (각속도)
    alpha_a, alpha_b: [rad/s²] (각가속도)
```

**물리적 이유**: 뉴턴 제2법칙 (F = ma, τ = Iα)이 SI 단위계를 기반으로 하므로, 수치 적분 시 rad 단위가 필수입니다.

### Rule 2: 입력 (Input)

**속도 및 가속도 입력은 가독성을 위해 deg 단위를 허용하되, 엔진 진입 시 즉시 rad으로 변환됩니다.**

```
입력 (Grid5DInput):
    v_a, v_b: [deg/s]          (각속도, 입력 단위)
    alpha_a, alpha_b: [deg/s²] (각가속도, 입력 단위)

변환 지점 (integrator_5d.py):
    v_a_rad = math.radians(v_a_deg)    # deg/s → rad/s
    alpha_a_rad = math.radians(alpha_a_deg)  # deg/s² → rad/s²
```

**변환 수식**:
```
v_rad = v_deg × (π / 180°)
α_rad = α_deg × (π / 180°)
```

### Rule 3: 출력 (Output, Projector)

**위상(rad)을 실제 각도(deg)나 좌표(m)로 투영하는 유일한 창구입니다.**

```
출력 (Grid5DOutput):
    theta_a, theta_b: [deg] (각도, 출력 단위)

변환 지점 (projector_5d.py):
    theta_a = math.degrees(phi_a)  # rad → deg
    theta_b = math.degrees(phi_b)  # rad → deg
```

**변환 수식**:
```
θ_deg = φ_rad × (180° / π)
```

---

## 📍 단위 변환 흐름도

```
[사용자 입력]                    [엔진 내부]                      [사용자 출력]
─────────────────              ─────────────────               ──────────────
Grid5DInput                     Grid5DState                     Grid5DOutput
  v_a: 0.5 [deg/s]   ────→      v_a: 0.0087 [rad/s]   ────→    theta_a: 0.5 [deg]
  alpha_a: 0.05 [deg/s²] ──→    alpha_a: 0.00087 [rad/s²] ─→   (projector에서 계산)
                                phi_a: 0.0087 [rad]
                              ↑                              ↓
                           [integrator]                  [projector]
                        math.radians()                 math.degrees()
```

---

## ⚠️ 주의사항

### 절대 금지 사항

1. ❌ **엔진 내부에서 deg 단위를 직접 사용**
   ```python
   # 잘못된 예
   state.v_a = 0.5  # [deg/s] - 절대 안 됨!
   
   # 올바른 예
   state.v_a = math.radians(0.5)  # [rad/s] - 올바름
   ```

2. ❌ **projector 없이 위상을 직접 deg로 변환**
   ```python
   # 잘못된 예
   theta_a = state.phi_a * 180 / math.pi  # 엔진 내부에서 직접 변환 - 절대 안 됨!
   
   # 올바른 예
   theta_a = projector.phase_to_coordinate(...)[3]  # projector 사용 - 올바름
   ```

### 권장 사항

1. ✅ **입력값은 항상 deg 단위로 제공**
   ```python
   inp = Grid5DInput(v_a=0.5, v_b=0.3)  # [deg/s] - 권장
   ```

2. ✅ **출력값은 projector를 통해서만 접근**
   ```python
   output = engine.step(inp)
   theta_a = output.theta_a  # [deg] - projector에서 변환됨
   ```

---

## 🔍 검증 방법

### 런타임 검증 (개발 모드)

개발 모드에서는 다음 검증을 수행할 수 있습니다:

```python
# integrator 내부 (예시)
assert input_data.v_a > -180.0 and input_data.v_a < 180.0, \
    f"v_a ({input_data.v_a})는 deg/s 단위여야 합니다. 범위: [-180, 180]"
```

### 테스트 검증

현재 53개 테스트가 모든 단위 변환을 검증합니다:
- `test_grid_5d_engine_uniform_motion`: deg → rad 변환 검증
- `test_grid_5d_engine_uniform_acceleration`: deg/s² → rad/s² 변환 검증
- `test_grid_5d_engine_coordinate_projection`: rad → deg 변환 검증

---

## 📚 참고 문서

- `docs/5D_CONCEPT_AND_EQUATIONS.md`: 5D 개념 및 수식
- `docs/NEWTONS_LAW_CONNECTION.md`: 뉴턴 제2법칙과의 연관성
- `docs/5AXIS_CNC_APPLICATION.md`: 5축 CNC 응용

---

**Author: GNJz**  
**Created: 2026-01-20**  
**Made in GNJz**  
**Version: v0.4.0-alpha (5D extension)**  
**License: MIT License**


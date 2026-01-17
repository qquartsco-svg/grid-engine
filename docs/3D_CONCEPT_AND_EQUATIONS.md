# 3D Grid Engine: 개념과 수식

## 개요

**Grid Engine 3D**는 **Ring X ⊗ Ring Y ⊗ Ring Z** 구조로 3차원 공간 위치 상태를 안정적으로 유지하는 엔진입니다.

2D Grid Engine의 자연스러운 확장이며, 동일한 물리 법칙과 수학적 구조를 3차원으로 확장합니다.

**작성자**: GNJz  
**작성 일자**: 2026-01-20  
**Made in GNJz**  
**Version**: v0.2.0 (3D extension)  
**License**: MIT License

---

## 1. 구조적 관계: 2D → 3D

### 1.1 2D Grid Engine (기존)

```
Grid 2D = Ring X ⊗ Ring Y

위상 공간: T² = S¹ × S¹ (토러스, 2차원)
상태: (φx, φy) ∈ [0, 2π) × [0, 2π) [rad²]
좌표: (x, y) [m]
```

### 1.2 3D Grid Engine (확장)

```
Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z

위상 공간: T³ = S¹ × S¹ × S¹ (토러스, 3차원)
상태: (φx, φy, φz) ∈ [0, 2π) × [0, 2π) × [0, 2π) [rad³]
좌표: (x, y, z) [m]
```

### 1.3 차이점 요약

| 항목 | 2D | 3D |
|------|-----|-----|
| **Ring 개수** | 2개 (X, Y) | 3개 (X, Y, Z) |
| **위상 공간** | T² (토러스 2차원) | T³ (토러스 3차원) |
| **상태 변수** | (φx, φy) | (φx, φy, φz) |
| **좌표** | (x, y) | (x, y, z) |
| **속도** | (vx, vy) | (vx, vy, vz) |
| **가속도** | (ax, ay) | (ax, ay, az) |

---

## 2. 수학적 표현

### 2.1 위상 공간 구조

#### 2D (기존)
```
위상 벡터: Φ = (φx, φy)
위상 공간: Φ ∈ T² = [0, 2π) × [0, 2π)
특징: 주기적 경계 조건 (φ ≡ φ + 2πn)
```

#### 3D (확장)
```
위상 벡터: Φ = (φx, φy, φz)
위상 공간: Φ ∈ T³ = [0, 2π) × [0, 2π) × [0, 2π)
특징: 각 차원마다 독립적인 주기적 경계 조건
```

### 2.2 좌표 변환

#### 2D 좌표 변환 (기존)
```
x = φx · (Lx / 2π)
y = φy · (Ly / 2π)

역변환:
φx = x · (2π / Lx)
φy = y · (2π / Ly)
```

#### 3D 좌표 변환 (확장)
```
x = φx · (Lx / 2π)
y = φy · (Ly / 2π)
z = φz · (Lz / 2π)  ← Z 방향 추가

역변환:
φx = x · (2π / Lx)
φy = y · (2π / Ly)
φz = z · (2π / Lz)  ← Z 방향 추가
```

**의미**:
- 각 차원(X, Y, Z)은 독립적으로 위상 → 좌표 변환
- 스케일 인자 Lx, Ly, Lz는 각 방향의 도메인 길이 [m]

---

## 3. 경로 통합 (Path Integration)

### 3.1 뉴턴 제2법칙 (3D)

#### 물리량 확장

| 물리량 | 2D | 3D |
|--------|-----|-----|
| **위치** r | (x, y) | (x, y, z) |
| **속도** v | (vx, vy) | (vx, vy, vz) |
| **가속도** a | (ax, ay) | (ax, ay, az) |
| **위상** φ | (φx, φy) | (φx, φy, φz) |

#### 뉴턴 2법칙 (벡터 형태)

```
F = ma  →  a = (ax, ay, az)

각 성분별:
  ax = dvx/dt
  ay = dvy/dt
  az = dvz/dt  ← Z 방향 추가
```

### 3.2 경로 통합 수식

#### 2D 경로 통합 (기존)

```
속도 업데이트:
  vx(t+Δt) = vx(t) + ax(t)·Δt
  vy(t+Δt) = vy(t) + ay(t)·Δt

위상 업데이트:
  φx(t+Δt) = φx(t) + vx(t)·Δt + ½ax(t)·Δt²
  φy(t+Δt) = φy(t) + vy(t)·Δt + ½ay(t)·Δt²
```

#### 3D 경로 통합 (확장)

```
속도 업데이트:
  vx(t+Δt) = vx(t) + ax(t)·Δt
  vy(t+Δt) = vy(t) + ay(t)·Δt
  vz(t+Δt) = vz(t) + az(t)·Δt  ← Z 방향 추가

위상 업데이트:
  φx(t+Δt) = φx(t) + vx(t)·Δt + ½ax(t)·Δt²
  φy(t+Δt) = φy(t) + vy(t)·Δt + ½ay(t)·Δt²
  φz(t+Δt) = φz(t) + vz(t)·Δt + ½az(t)·Δt²  ← Z 방향 추가
```

**핵심**: 각 차원(X, Y, Z)은 **독립적으로** 뉴턴 2법칙을 따릅니다.

### 3.3 Semi-implicit Euler 방법 (3D)

#### 코드 수식

```python
# 시간 단위 변환 (물리 법칙 적용을 위해 필수)
dt_s = dt_ms / 1000.0  # [ms] → [s]

# 속도 업데이트 (뉴턴 2법칙)
if a_x is not None:
    vx_new = vx_old + ax * dt_s
else:
    vx_new = vx_input

if a_y is not None:
    vy_new = vy_old + ay * dt_s
else:
    vy_new = vy_input

if a_z is not None:
    vz_new = vz_old + az * dt_s  # Z 방향 추가
else:
    vz_new = vz_input  # Z 방향 추가

# 위상 업데이트 (경로 통합)
if a_x is not None:
    dphi_x = vx_old * dt_s + 0.5 * ax * dt_s²
else:
    dphi_x = vx_input * dt_s

if a_y is not None:
    dphi_y = vy_old * dt_s + 0.5 * ay * dt_s²
else:
    dphi_y = vy_input * dt_s

if a_z is not None:
    dphi_z = vz_old * dt_s + 0.5 * az * dt_s²  # Z 방향 추가
else:
    dphi_z = vz_input * dt_s  # Z 방향 추가

# 새로운 위상
phi_x_new = phi_x_old + dphi_x
phi_y_new = phi_y_old + dphi_y
phi_z_new = phi_z_old + dphi_z  # Z 방향 추가
```

---

## 4. 물리적 해석

### 4.1 3D 공간에서의 뉴턴 2법칙

#### 상태 방정식 (3D)

```
상태 변수:
  - φx(t): X 방향 위상 [rad]
  - φy(t): Y 방향 위상 [rad]
  - φz(t): Z 방향 위상 [rad]
  - vx(t): X 방향 속도 [m/s]
  - vy(t): Y 방향 속도 [m/s]
  - vz(t): Z 방향 속도 [m/s]

동역학:
  dφx/dt = vx(t)
  dφy/dt = vy(t)
  dφz/dt = vz(t)  ← Z 방향 추가
  
  dvx/dt = ax(t)  ← 뉴턴 2법칙
  dvy/dt = ay(t)  ← 뉴턴 2법칙
  dvz/dt = az(t)  ← 뉴턴 2법칙 (Z 방향 추가)
```

#### 벡터 형태

```
위상 벡터: Φ = (φx, φy, φz)
속도 벡터: v = (vx, vy, vz)
가속도 벡터: a = (ax, ay, az)

동역학:
  dΦ/dt = v
  dv/dt = a  ← 뉴턴 2법칙 (벡터 형태)
```

### 4.2 에너지 함수 (3D)

#### 2D 에너지 (기존)

```
E_2D = Ex + Ey
     = ½(φx² + φy²) + ½(vx² + vy²)
     
각 성분:
  Ex = ½φx² + ½vx²  (X 방향 에너지)
  Ey = ½φy² + ½vy²  (Y 방향 에너지)
```

#### 3D 에너지 (확장)

```
E_3D = Ex + Ey + Ez
     = ½(φx² + φy² + φz²) + ½(vx² + vy² + vz²)
     
각 성분:
  Ex = ½φx² + ½vx²  (X 방향 에너지)
  Ey = ½φy² + ½vy²  (Y 방향 에너지)
  Ez = ½φz² + ½vz²  (Z 방향 에너지, 새로 추가)
```

**의미**:
- 각 차원(X, Y, Z)은 독립적인 에너지를 가집니다.
- 총 에너지는 각 방향 에너지의 합입니다.
- Ring Attractor는 각 방향을 독립적으로 안정화합니다.

---

## 5. Ring Attractor 연관성 (3D)

### 5.1 Ring ⊗ Ring ⊗ Ring 구조

#### 2D (기존)
```
Grid 2D = Ring X ⊗ Ring Y

각 Ring은 독립적으로:
  - 위상 안정화
  - 노이즈 억제
  - 에너지 최소화
```

#### 3D (확장)
```
Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z

각 Ring은 독립적으로:
  - Ring X: X 방향 위상 안정화
  - Ring Y: Y 방향 위상 안정화
  - Ring Z: Z 방향 위상 안정화 (새로 추가)
```

### 5.2 위상 안정화 흐름 (3D)

```
입력: (φx, φy, φz) - 수치 적분으로 계산된 위상

1. Ring X 안정화:
   - 위상 φx → Ring X 인덱스로 변환
   - Ring X 실행 (Attractor 동역학)
   - 안정화된 φx' 반환

2. Ring Y 안정화:
   - 위상 φy → Ring Y 인덱스로 변환
   - Ring Y 실행 (Attractor 동역학)
   - 안정화된 φy' 반환

3. Ring Z 안정화 (새로 추가):
   - 위상 φz → Ring Z 인덱스로 변환
   - Ring Z 실행 (Attractor 동역학)
   - 안정화된 φz' 반환

출력: (φx', φy', φz') - 안정화된 위상
```

### 5.3 에너지 최소화 (3D)

#### Ring 에너지 (각 방향별)

```
E_ring_x = -Σ wij * ai * aj  (Ring X의 Mexican-hat topology)
E_ring_y = -Σ wij * ai * aj  (Ring Y의 Mexican-hat topology)
E_ring_z = -Σ wij * ai * aj  (Ring Z의 Mexican-hat topology, 새로 추가)
```

#### Grid 3D 에너지

```
E_grid_3d = E_ring_x + E_ring_y + E_ring_z + E_kinetic

여기서:
  E_kinetic = ½(vx² + vy² + vz²)  (운동 에너지)
```

**의미**:
- 각 Ring은 자체적으로 에너지를 최소화합니다.
- X, Y, Z 방향이 독립적으로 안정화됩니다.
- 총 에너지는 각 방향 에너지의 합입니다.

---

## 6. 열역학적 해석 (3D)

### 6.1 엔트로피 관점

#### 2D (기존)
```
외란 → 위상 공간 흡수 (T²) → 국소적 엔트로피 감소
```

#### 3D (확장)
```
외란 → 위상 공간 흡수 (T³) → 국소적 엔트로피 감소
```

**의미**:
- 3D 공간에서 외란(노이즈)은 3차원 위상 공간에서 흡수됩니다.
- 각 Ring이 독립적으로 외란을 흡수합니다.
- 결과적으로 3D 공간에서 국소적 질서가 유지됩니다.

### 6.2 마모 감소 메커니즘 (3D)

#### 2D (기존)
```
일반 PID 제어:
  외란 → 급격한 제어 신호 → 급격한 (ax, ay) 변화 → 진동/마모

Grid 2D 제어:
  외란 → 점진적 위상 변화 (Ring X, Y 안정화) → 부드러운 (ax, ay) 변화 → 마모 감소
```

#### 3D (확장)
```
일반 PID 제어:
  외란 → 급격한 제어 신호 → 급격한 (ax, ay, az) 변화 → 진동/마모

Grid 3D 제어:
  외란 → 점진적 위상 변화 (Ring X, Y, Z 안정화) → 부드러운 (ax, ay, az) 변화 → 마모 감소
```

**3D의 장점**:
- 3차원 공간에서의 진동/노이즈 억제
- 모든 방향에서 부드러운 제어
- 3D 공간에서의 기계적 부하 감소

---

## 7. 실제 응용 예시

### 7.1 드론 위치 추적

```
물리적 과정:
  1. 추력 (F) → 가속도 (a = (ax, ay, az))
  2. 가속도 적분 → 속도 (v = (vx, vy, vz))
  3. 속도 적분 → 위치 (r = (x, y, z))

Grid 3D Engine 적용:
  - 입력: 가속도 a = (ax, ay, az) (IMU 데이터)
  - 내부: 경로 통합 (뉴턴 2법칙, 3D)
  - 출력: 안정화된 위치 (x, y, z) (Ring X, Y, Z 안정화)
```

### 7.2 3D 로봇 팔 제어

```
물리적 과정:
  1. 관절 토크 (τ) → 각가속도 (α)
  2. 각가속도 적분 → 각속도 (ω)
  3. 각속도 적분 → 관절 각도 (θ)
  4. 관절 각도 → 엔드 이펙터 위치 (x, y, z)

Grid 3D Engine 적용:
  - 입력: 각가속도 α (관절별)
  - 내부: 경로 통합 (회전 역학, 3D)
  - 출력: 안정화된 엔드 이펙터 위치 (x, y, z)
```

### 7.3 잠수함 수심 제어

```
물리적 과정:
  1. 부력 제어 (F) → 수직 가속도 (az)
  2. 가속도 적분 → 수직 속도 (vz)
  3. 속도 적분 → 수심 (z)

Grid 3D Engine 적용:
  - 입력: 가속도 a = (ax, ay, az) (수평 + 수직)
  - 내부: 경로 통합 (뉴턴 2법칙, 3D)
  - 출력: 안정화된 위치 (x, y, z) (수평 + 수심)
```

---

## 8. 코드 구조 비교

### 8.1 2D vs 3D 모듈

| 모듈 | 2D | 3D |
|------|-----|-----|
| **타입** | `types.py` | `types_3d.py` |
| **설정** | `config.py` | `config_3d.py` |
| **적분기** | `integrator.py` | `integrator_3d.py` |
| **어댑터** | `ring_adapter.py` | `ring_3d_adapter.py` |
| **프로젝터** | `projector.py` | `projector_3d.py` |
| **엔진** | `grid_engine.py` | `grid_3d_engine.py` |

### 8.2 코드 재사용성

**공통 모듈** (2D와 3D 모두 사용):
- `coupling.py` - 위상 정규화 (차원 독립적)
- `energy.py` - 에너지 계산 (차원 독립적, 확장 필요)

**차원별 모듈** (2D와 3D 분리):
- 타입 정의 (2D: 2개 변수, 3D: 3개 변수)
- 적분기 (2D: 2차원, 3D: 3차원)
- Ring Adapter (2D: 2개 Ring, 3D: 3개 Ring)
- Projector (2D: 2D 좌표, 3D: 3D 좌표)

---

## 9. 수식 요약

### 9.1 핵심 수식 (3D)

```
위상 공간: T³ = [0, 2π) × [0, 2π) × [0, 2π)

상태 방정식:
  dφx/dt = vx
  dφy/dt = vy
  dφz/dt = vz  ← Z 방향 추가
  
  dvx/dt = ax  ← 뉴턴 2법칙
  dvy/dt = ay  ← 뉴턴 2법칙
  dvz/dt = az  ← 뉴턴 2법칙 (Z 방향 추가)

좌표 변환:
  x = φx · (Lx / 2π)
  y = φy · (Ly / 2π)
  z = φz · (Lz / 2π)  ← Z 방향 추가

에너지 함수:
  E = ½(φx² + φy² + φz²) + ½(vx² + vy² + vz²)
```

### 9.2 Semi-implicit Euler (3D)

```
시간 단위: dt_s = dt_ms / 1000.0 [s]

속도 업데이트:
  vx_new = vx_old + ax * dt_s
  vy_new = vy_old + ay * dt_s
  vz_new = vz_old + az * dt_s  ← Z 방향 추가

위상 업데이트:
  φx_new = φx_old + vx_old * dt_s + 0.5 * ax * dt_s²
  φy_new = φy_old + vy_old * dt_s + 0.5 * ay * dt_s²
  φz_new = φz_old + vz_old * dt_s + 0.5 * az * dt_s²  ← Z 방향 추가
```

---

## 10. 결론

### 핵심 메시지

1. **3D = Ring ⊗ Ring ⊗ Ring**: 2D의 자연스러운 확장
2. **독립성**: 각 차원(X, Y, Z)은 독립적으로 동작
3. **물리 법칙**: 뉴턴 2법칙이 각 차원에 독립적으로 적용
4. **안정화**: 각 Ring이 독립적으로 위상 안정화

### 수식 요약

```
구조: Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z
상태: (φx, φy, φz) ∈ T³
좌표: (x, y, z) = (φx·Lx/2π, φy·Ly/2π, φz·Lz/2π)
동역학: dΦ/dt = v, dv/dt = a (뉴턴 2법칙)
에너지: E = ½(φ² + v²) (각 방향 합)
```

### 실용적 의미

Grid 3D Engine을 사용하면:
- ✅ 3차원 공간에서 위치 추적
- ✅ 3D 진동/노이즈 억제
- ✅ 모든 방향에서 부드러운 제어
- ✅ 물리 법칙 기반 (뉴턴 2법칙)

---

**작성자**: GNJz  
**작성 일자**: 2026-01-20  
**Made in GNJz**  
**Version**: v0.2.0 (3D extension)  
**License**: MIT License


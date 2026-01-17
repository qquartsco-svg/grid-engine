# Grid Engine 아키텍처

## 구조 개요

Grid Engine은 **Ring Attractor Engine을 기반으로 구축된 2D 위상 공간 시스템**입니다.

```
┌─────────────────────────────────────────────────────────┐
│                    Grid Engine                           │
│  (2D Phase Space: Ring ⊗ Ring)                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐            │
│  │ Ring Engine  │         │ Ring Engine  │            │
│  │    (X축)     │         │    (Y축)     │            │
│  │  φx ∈ [0,2π) │         │  φy ∈ [0,2π) │            │
│  └──────┬───────┘         └──────┬───────┘            │
│         │                        │                      │
│         └────────┬──────────────┘                      │
│                  │                                      │
│         ┌────────▼────────┐                            │
│         │  Coupling Layer │                            │
│         │  (위상 → 좌표)  │                            │
│         └─────────────────┘                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 핵심 개념: Ring ⊗ Ring (직교 결합)

Grid Engine은 **두 개의 독립적인 Ring Attractor를 직교(orthogonal)로 결합**한 구조입니다.

### 수학적 표현

```
Grid = Ring_x ⊗ Ring_y

위상 공간:
  φx(t) ∈ [0, 2π)  ← X 방향 Ring
  φy(t) ∈ [0, 2π)  ← Y 방향 Ring

좌표 변환:
  x = φx · (Lx / 2π)
  y = φy · (Ly / 2π)
```

## 계층 구조

### 1. 최상위: Grid Engine
- **책임**: 2D 위상 상태 관리, 경로 통합(Path Integration)
- **입력**: 속도(v_x, v_y), 가속도(a_x, a_y)
- **출력**: 위상(φx, φy), 좌표(x, y)

### 2. 중간 계층: Ring Adapter
- **책임**: Ring Engine 호출 래핑, 의존성 경계
- **구성**: 
  - `RingAdapter` 클래스
  - X, Y 방향 각각의 `RingAttractorEngine` 인스턴스

### 3. 하위 계층: Ring Attractor Engine
- **책임**: 1D 위상 안정화, Attractor 동역학
- **입력**: 위상 값 (인덱스로 변환)
- **출력**: 안정화된 위상 (center)

## 데이터 흐름

### Step 함수 실행 순서

```
1. 입력 수신
   └─> GridInput(v_x, v_y, a_x, a_y)

2. 수치 적분 (Semi-implicit Euler)
   └─> integrator.py::semi_implicit_euler()
       ├─> 속도 업데이트: v(t+Δt) = v(t) + a·Δt
       └─> 위상 업데이트: φ(t+Δt) = φ(t) + v·Δt + ½a·Δt²
       └─> 반환: (new_phi_x, new_phi_y, new_v_x, new_v_y)

3. Ring 안정화
   └─> ring_adapter.py::step()
       ├─> 위상 → Ring 인덱스 변환
       │   └─> idx_x = (φx / 2π) * size
       │   └─> idx_y = (φy / 2π) * size
       │
       ├─> X 방향 Ring 실행
       │   └─> ring_x.inject(direction_idx=idx_x)
       │   └─> ring_x.run(duration_ms=dt_ms)
       │   └─> state_x = ring_x.get_state()
       │
       ├─> Y 방향 Ring 실행
       │   └─> ring_y.inject(direction_idx=idx_y)
       │   └─> ring_y.run(duration_ms=dt_ms)
       │   └─> state_y = ring_y.get_state()
       │
       └─> Ring center → 위상 변환
           └─> stabilized_phi_x = (state_x.center / size) * 2π
           └─> stabilized_phi_y = (state_y.center / size) * 2π
           └─> 가중 평균: 90% 원래 위상 + 10% Ring 조정

4. 상태 업데이트
   └─> coupling.py::update_state_from_phases()
       ├─> 위상 정규화: φ ∈ [0, 2π)
       ├─> 좌표 변환: x = φx · (scale / 2π)
       └─> GridState 생성

5. 출력 생성
   └─> GridOutput(phi_x, phi_y, x, y, ...)
```

## 상세 로직 설명

### 1. 수치 적분 단계

**목적**: 물리 법칙에 따른 위상 업데이트

```python
# Semi-implicit Euler
new_v_x = v_x + a_x * dt_ms
new_phi_x = phi_x + v_x * dt_ms + 0.5 * a_x * dt_ms²
```

**의미**: 
- 뉴턴 2법칙 (F=ma) 적용
- 경로 통합(Path Integration) 수행
- 외부 입력(속도, 가속도)을 위상 변화로 변환

### 2. Ring 안정화 단계

**목적**: 위상을 Attractor manifold에 "붙잡기"

```python
# 위상을 Ring 인덱스로 변환
idx_x = int((phi_x / 2π) * ring_size) % ring_size

# Ring에 주입 (위상 "설정")
ring_x.inject(direction_idx=idx_x, strength=0.8)

# Ring 동역학 실행 (안정화)
state_x = ring_x.run(duration_ms=dt_ms)

# Ring center를 위상으로 변환
stabilized_phi_x = (state_x.center / ring_size) * 2π
```

**의미**:
- Ring Attractor는 위상을 "끌어당김" (attraction)
- 노이즈/외란에 강건함
- 위상이 "흐트러지지 않도록" 유지

### 3. 좌표 변환 단계

**목적**: 내부 위상을 외부 좌표로 투영

```python
# 위상 → 좌표 변환
x = phi_x * (spatial_scale_x / 2π)
y = phi_y * (spatial_scale_y / 2π)
```

**의미**:
- 위상은 내부 상태 (Grid Engine 책임)
- 좌표는 관측자 책임 (상위 시스템)
- **중요**: Grid Engine은 좌표를 "계산"하지 않고, 위상만 유지

## 의존성 관계

```
Grid Engine
    │
    ├─> Ring Adapter (의존성 경계)
    │       │
    │       ├─> Ring Attractor Engine (X)
    │       │       └─> HippoMemoryV4System
    │       │           └─> CA3 Neurons
    │       │
    │       └─> Ring Attractor Engine (Y)
    │               └─> HippoMemoryV4System
    │                   └─> CA3 Neurons
    │
    ├─> Integrator (독립 모듈)
    │       └─> semi_implicit_euler()
    │
    ├─> Coupling (독립 모듈)
    │       ├─> phase_to_coordinate()
    │       └─> update_state_from_phases()
    │
    └─> Energy (진단용, 선택적)
            └─> calculate_energy()
```

## 핵심 설계 원칙

### 1. 책임 분리 (Separation of Concerns)

- **Grid Engine**: 2D 위상 상태 관리
- **Ring Engine**: 1D 위상 안정화
- **Coupling**: 위상 ↔ 좌표 변환
- **Integrator**: 수치 적분

### 2. 의존성 역전 (Dependency Inversion)

- Grid Engine은 Ring 내부 구현을 모름
- Ring Adapter가 경계 역할
- Ring Engine은 독립적으로 교체 가능

### 3. 관측자 패턴 (Observer Pattern)

- Grid Engine은 위상만 유지
- 좌표 투영은 상위 시스템(관측자) 책임
- "엔진은 상태를 유지하고, 관측자가 해석한다"

## 물리학적 해석

### 뉴턴 2법칙 연결

```
F = ma  →  a = dv/dt  →  v = dx/dt

Grid Engine:
  - 가속도(a) 입력 → 속도(v) 적분
  - 속도(v) 입력 → 위상(φ) 적분
  - 위상(φ) → 좌표(x) 변환
```

### 열역학 연결

```
Ring Attractor = 에너지 최소화

Grid Engine:
  - 외란 → 위상 변화
  - Ring → 위상 안정화 (에너지 감소)
  - 결과: 국소적 엔트로피 감소
```

## 실제 사용 예시

```python
# 1. Grid Engine 초기화
engine = GridEngine(initial_x=0.0, initial_y=0.0)

# 2. 속도 입력
inp = GridInput(v_x=1.0, v_y=0.0)
output = engine.step(inp)

# 내부 동작:
#   - integrator: phi_x += 1.0 * dt
#   - ring_x: 위상 안정화
#   - coupling: x = phi_x * scale

# 3. 결과
print(f"위상: {output.phi_x} rad")  # 내부 상태
print(f"좌표: {output.x} m")         # 관측 좌표
```

## 요약

**Grid Engine = Ring ⊗ Ring + 경로 통합**

- **Ring**: 위상 안정화 (1D)
- **Grid**: 위상 공간 확장 (2D)
- **Integrator**: 물리 법칙 적용
- **Coupling**: 위상 ↔ 좌표 변환

**핵심 메시지**: 
"Grid Engine은 위치를 계산하지 않는다. 
위치 상태가 흐트러지지 않도록 유지할 뿐이다."


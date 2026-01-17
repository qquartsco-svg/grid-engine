# Grid Engine과 Ring Attractor의 연관성

## 개요

**Grid Engine**은 **Ring Attractor Engine**을 2차원으로 확장한 구조입니다.

이 문서는 Grid Engine이 Ring Attractor와 어떻게 연결되는지, 그리고 두 엔진의 관계를 설명합니다.

**작성자**: GNJz  
**작성 일자**: 2026-01-20  
**Version**: v0.1.1  
**Made in GNJz**  
**License**: MIT License

---

## 1. 구조적 관계: Grid = Ring ⊗ Ring

### 1.1 핵심 개념

Grid Engine은 **Ring Attractor의 직교 결합(Tensor Product)**입니다:

```
Grid Engine = Ring X ⊗ Ring Y
```

**의미**:
- **Ring X**: X 방향 위상 관리 (φx ∈ [0, 2π))
- **Ring Y**: Y 방향 위상 관리 (φy ∈ [0, 2π))
- **직교 결합**: 각 Ring은 독립적으로 동작하지만, 함께 2D 공간을 구성

### 1.2 수학적 표현

#### Ring Attractor (1D)
```
상태: φ(t) ∈ [0, 2π) [rad]
동역학: dφ/dt = v(t) + noise
```

#### Grid Engine (2D)
```
상태: (φx(t), φy(t)) ∈ [0, 2π) × [0, 2π) [rad²]
동역학:
  dφx/dt = vx(t) + noise
  dφy/dt = vy(t) + noise
```

---

## 2. 구현 관점에서의 연결

### 2.1 Ring Adapter 패턴

Grid Engine은 **Ring Attractor Engine을 직접 사용**합니다:

```python
# grid_engine/adapters/ring_adapter.py

class RingAdapter:
    """
    Ring Attractor Engine 래퍼
    
    Grid Engine은 Ring 내부 구현을 몰라야 함 (호출만)
    Adapter 패턴을 통해 의존성을 역전시킵니다.
    """
    
    def __init__(self, config: RingAdapterConfig):
        # Ring Attractor Engine 생성
        self.ring_x = RingAttractorEngine(...)  # X 방향
        self.ring_y = RingAttractorEngine(...)  # Y 방향
    
    def step(self, phi: float) -> float:
        """
        Ring Attractor를 통해 위상 안정화
        
        입력: 현재 위상 φ
        출력: 안정화된 위상 φ_stabilized
        """
        # Ring Attractor의 step() 호출
        output = self.ring_x.step(...)
        return output.center_phase
```

### 2.2 코드 구조

```
Grid Engine (grid_engine.py)
  ↓
Ring Adapter (adapters/ring_adapter.py)
  ↓
Ring Attractor Engine (외부 패키지: ring-attractor-engine)
```

**의존성**:
- Grid Engine → Ring Adapter (의존)
- Ring Adapter → Ring Attractor Engine (의존)
- Grid Engine → Ring Attractor Engine (간접 의존, Adapter를 통해)

---

## 3. 동역학적 연결

### 3.1 위상 안정화 흐름

#### Ring Attractor의 역할

1. **위상 상태 유지**: 외부 입력이 없어도 위상을 기억
2. **노이즈 필터링**: 외란을 흡수하여 안정화
3. **Attractor 동역학**: 위상을 최소 에너지 상태로 끌어당김

#### Grid Engine에서의 활용

```python
# grid_engine/grid_engine.py

def step(self, input_data: GridInput) -> GridOutput:
    """
    Grid Engine step 함수
    
    알고리즘:
        1. 수치 적분: 속도/가속도 → 위상 업데이트 (뉴턴 2법칙)
        2. Ring 안정화: 위상을 Attractor에 붙잡기
        3. 좌표 투영: 위상 → 좌표 변환
    """
    # 1. 수치 적분 (뉴턴 2법칙)
    new_phi_x, new_phi_y, new_v_x, new_v_y = semi_implicit_euler(...)
    
    # 2. Ring 안정화 (Ring Attractor 호출)
    stabilized_phi_x = self.ring_adapter_x.step(new_phi_x)
    stabilized_phi_y = self.ring_adapter_y.step(new_phi_y)
    
    # 3. 좌표 투영 (관측자 패턴)
    x, y = self.projector.phase_to_coordinate(stabilized_phi_x, stabilized_phi_y)
    
    return GridOutput(x=x, y=y, phi_x=stabilized_phi_x, phi_y=stabilized_phi_y)
```

### 3.2 에너지 최소화

#### Ring Attractor의 에너지 함수

```
E_ring = -Σ wij * ai * aj  (Mexican-hat topology)
```

#### Grid Engine의 에너지 함수

```
E_grid = E_x + E_y = E_ring_x + E_ring_y + E_kinetic
```

**연결점**:
- Grid Engine의 에너지는 각 Ring의 에너지 합
- X, Y 방향이 독립적으로 에너지 최소화

---

## 4. 물리적 해석

### 4.1 위상 공간 구조

#### Ring Attractor (1D)
```
위상 공간: S¹ (원형, 1차원)
상태: φ ∈ [0, 2π)
특징: 주기적 경계 조건
```

#### Grid Engine (2D)
```
위상 공간: T² = S¹ × S¹ (토러스, 2차원)
상태: (φx, φy) ∈ [0, 2π) × [0, 2π)
특징: X, Y 방향 모두 주기적 경계 조건
```

### 4.2 공간 표현

#### Ring Attractor
```
1D 위치: x = φ · (L / 2π)
  여기서 L은 도메인 길이 [m]
```

#### Grid Engine
```
2D 위치: 
  x = φx · (Lx / 2π)
  y = φy · (Ly / 2π)
  
  여기서 Lx, Ly는 각 방향의 도메인 길이 [m]
```

---

## 5. 모듈 분리 원칙

### 5.1 책임 분리

| 모듈 | 역할 | Ring Attractor 연관성 |
|------|------|---------------------|
| `grid_engine.py` | 조립 + step() | Ring Adapter 호출 |
| `adapters/ring_adapter.py` | Ring 래핑 | Ring Attractor Engine 직접 사용 |
| `integrator.py` | 수치 적분 | 독립적 (Ring과 무관) |
| `coupling.py` | 위상 정규화 | 독립적 (Ring과 무관) |
| `projector.py` | 좌표 투영 | 독립적 (Ring과 무관) |
| `energy.py` | 에너지 계산 | Ring 에너지 포함 가능 |

### 5.2 의존성 경계

```
Grid Engine Core
  ├── Ring Adapter (의존)
  │     └── Ring Attractor Engine (외부 패키지)
  ├── Integrator (독립)
  ├── Coupling (독립)
  ├── Projector (독립)
  └── Energy (독립, Ring 에너지 선택적 포함)
```

**원칙**:
- Grid Engine Core는 Ring Adapter만 직접 의존
- Ring Adapter는 Ring Attractor Engine만 의존
- 다른 모듈(Integrator, Coupling, Projector, Energy)은 Ring과 독립적

---

## 6. 확장 가능성

### 6.1 3D 확장

```
Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z
```

**구현**:
- Ring Z 추가
- Ring Adapter Z 추가
- 3D 위상 공간 구성

### 6.2 N차원 확장

```
Grid N-D = Ring 1 ⊗ Ring 2 ⊗ ... ⊗ Ring N
```

**구현**:
- N개 Ring 생성
- N개 Ring Adapter 생성
- N차원 위상 공간 구성

### 6.3 5축 CNC 적용 예시

```
Grid 5D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B

축 매핑:
  - Ring X, Y, Z: 선형 축 (이동)
  - Ring A, B: 회전 축 (각도)
```

---

## 7. 코드 예시

### 7.1 Grid Engine에서 Ring 사용

```python
from grid_engine import GridEngine, GridInput

# Grid Engine 생성 (내부적으로 Ring X, Y 생성)
engine = GridEngine(initial_x=0.0, initial_y=0.0)

# 입력 (속도/가속도)
inp = GridInput(v_x=1.0, v_y=0.0, a_x=0.1, a_y=0.0)

# Step 실행 (내부적으로 Ring X, Y의 step() 호출)
output = engine.step(inp)

# 출력
print(f"위상: ({output.phi_x:.2f}, {output.phi_y:.2f})")  # Ring이 안정화한 위상
print(f"좌표: ({output.x:.2f}, {output.y:.2f})")  # Projector가 변환한 좌표
```

### 7.2 Ring Adapter 내부 동작

```python
# adapters/ring_adapter.py 내부

class RingAdapter:
    def step(self, phi: float) -> float:
        """
        Ring Attractor를 통해 위상 안정화
        
        내부 동작:
            1. 현재 위상 φ를 Ring Attractor에 입력
            2. Ring Attractor가 Attractor 동역학으로 안정화
            3. 안정화된 위상 φ_stabilized 반환
        """
        # Ring Attractor Engine의 step() 호출
        ring_output = self.ring_engine.step(...)
        
        # 안정화된 위상을 반환 (90% 원본 + 10% Ring 조정)
        stabilized_phi = 0.9 * phi + 0.1 * ring_output.center_phase
        
        return stabilized_phi
```

---

## 8. 결론

### 핵심 메시지

1. **Grid Engine = Ring ⊗ Ring**: 구조적 직교 결합
2. **Ring Adapter 패턴**: 의존성 역전을 통한 모듈화
3. **독립적 확장**: N차원으로 자연스럽게 확장 가능
4. **물리적 일관성**: 뉴턴 2법칙 + Attractor 동역학

### 관계 다이어그램

```
┌─────────────────────────────────────┐
│         Grid Engine (2D)            │
│  ┌───────────────────────────────┐  │
│  │  Ring X ⊗ Ring Y              │  │
│  │  ┌──────────┐   ┌──────────┐ │  │
│  │  │ Ring X   │ ⊗ │ Ring Y   │ │  │
│  │  │ Adapter  │   │ Adapter  │ │  │
│  │  └────┬─────┘   └────┬─────┘ │  │
│  └───────┼───────────────┼───────┘  │
└──────────┼───────────────┼──────────┘
           │               │
           ▼               ▼
    ┌──────────┐   ┌──────────┐
    │ Ring     │   │ Ring     │
    │ Attractor│   │ Attractor│
    │ Engine   │   │ Engine   │
    └──────────┘   └──────────┘
    (외부 패키지)   (외부 패키지)
```

### 실용적 의미

Grid Engine을 사용하면:
- ✅ Ring Attractor의 안정성 활용 (위상 기억)
- ✅ 2D 공간 확장 (Ring ⊗ Ring)
- ✅ N차원 자연스러운 확장 (Ring ⊗ ... ⊗ Ring)
- ✅ 물리적 일관성 (뉴턴 2법칙 + Attractor)

---

**작성자**: GNJz  
**작성 일자**: 2026-01-20  
**Version**: v0.1.1  
**Made in GNJz**  
**License**: MIT License


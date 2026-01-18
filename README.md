# Grid Engine

**Grid Engine - 2D/3D 공간 상태 메모리 엔진**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.3.0--alpha-blue.svg)](https://github.com/qquartsco-svg/grid-engine)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/qquartsco-svg/grid-engine)

**English**: [README_EN.md](README_EN.md)

---

## 🎯 무엇을 하는가

**Grid Engine**은 Ring Attractor를 직교 결합하여 2D/3D/4D/5D 공간 위치 상태를 안정적으로 유지하는 **정밀 운동 제어 엔진**입니다.

**⚠️ 현재 상태**: 이 프로젝트는 **시뮬레이션 및 이론 검증 단계**입니다. 벤치마크 초기 결과가 도출되었으며, **지속적인 검증과 개선이 진행 중**입니다. 코드는 수학적 모델의 정확성을 검증하는 단계이며, 실제 적용 시 추가 검증이 필요합니다.

**핵심 전략**: 기존 제어 시스템을 대체하는 것이 아니라, **침투(Infiltration)**하여 효과를 극대화하는 것을 목표로 합니다. 독립적이지만 호환성이 좋은 모듈러 설계로, 기존 시스템과의 통합을 고려한 설계입니다.

---

## 📐 차원별 확장 및 활용 분야

### 2D Grid Engine: 평면 운동 제어

**구조**: `Grid = Ring X ⊗ Ring Y`

**위상 공간**: T² = S¹ × S¹ (2차원 토러스)

**잠재적 활용 분야** (이론 검증 단계):
- 🔬 **평면 로봇**: 2축 이동 로봇, XY 테이블 (시뮬레이션)
- 🔬 **평면 가공**: 2D 레이저 커팅, 플롯터 (개념 검증)
- 🔬 **항법 시스템**: 2D 위치 추적, GPS 보정 (연구 단계)
- 🔬 **게임/시뮬레이션**: 2D 캐릭터 이동, 물리 엔진 (시뮬레이션)

**특징**:
- 가장 기본적인 공간 상태 메모리
- X, Y 두 방향의 독립적인 Ring Attractor
- 경로 통합을 통한 자기 중심 위치 추적

---

### 3D Grid Engine: 3차원 공간 운동 제어

**구조**: `Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z`

**위상 공간**: T³ = S¹ × S¹ × S¹ (3차원 토러스)

**잠재적 활용 분야** (이론 검증 단계):
- 🔬 **3축 CNC 가공**: 밀링, 드릴링, 선반 (이론적 모델)
- 🔬 **3D 프린터**: 적층 제조, 정밀 출력 (시뮬레이션)
- 🔬 **드론/항공기**: 3D 위치 제어, 자세 안정화 (연구 단계)
- 🔬 **로봇 팔 (3축)**: 기본 팔 이동, 픽 앤 플레이스 (개념 검증)
- 🔬 **항법 시스템**: 3D SLAM, 위치 추적 (이론 검증)
- 🔬 **가상 현실**: 3D 공간 내 이동, 물리 시뮬레이션 (시뮬레이션)

**특징**:
- 2D에서 Z축 추가로 3차원 공간 확장
- 높이(깊이) 제어 추가
- 나선형 궤적 및 복잡한 3D 경로 생성 가능

---

### 4D Grid Engine: 4차원 확장 운동 제어

**구조**: `Grid 4D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W`

**위상 공간**: T⁴ = S¹ × S¹ × S¹ × S¹ (4차원 토러스)

**잠재적 활용 분야** (이론 검증 단계):
- 🔬 **4축 CNC 가공**: 회전 테이블 포함 가공 (이론적 모델)
- 🔬 **시간-공간 제어**: 시간에 따른 3D 경로 제어 (개념 검증)
- 🔬 **다중 작업 공간**: 여러 작업 영역 동시 제어 (연구 단계)
- 🔬 **고차원 제어**: 4차원 상태 공간 제어 (이론 검증)
- 🔬 **연구/실험**: 4차원 위상 공간 탐색 (시뮬레이션)

**특징**:
- 3D에서 W축 추가로 4차원 확장
- 시간 또는 추가 공간 차원 제어
- 고차원 위상 공간 탐색

---

### 5D Grid Engine: CNC급 정밀 움직임 → 로봇 일반 움직임 확장

**구조**: `Grid 5D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B`

**위상 공간**: T⁵ = S¹ × S¹ × S¹ × S¹ × S¹ (5차원 토러스)

**핵심 아이디어**: 
> **5D Grid Engine은 5축 CNC 가공기의 정밀 움직임 개념에서 시작하여, 모든 로봇의 일반 움직임에 적용 가능한 범용 정밀 제어 엔진입니다.**

**구성**:
- **위치 3축** (X, Y, Z): 선형 이동 [m]
- **회전 2축** (A, B): 각도 회전 [deg]

---

#### 📊 활용 방안 분석

**1. 연구용 가치** (이론 검증 단계)

**학술적 의미**:
- 🔬 **5차원 위상 공간 제어**: T⁵ 토러스에서의 상태 안정화 이론
- 🔬 **Ring Attractor 직교 결합**: 5개 독립 Ring의 수학적 결합
- 🔬 **뉴턴 2법칙 확장**: 5축에서의 경로 통합 (F=ma)
- 🔬 **위상 메모리**: 외란 후 복귀 메커니즘 (수학적 모델)

**연구 응용 분야**:
- 🔬 **5축 CNC 가공**: 정밀 부품 가공, 복잡한 형상 제조 (이론적 모델)
- 🔬 **회전축 시스템**: 로터리 엔진, 원자력 제어봉 (개념 검증)
- 🔬 **항공우주**: 위성 자세 제어, 로켓 추진 방향 제어 (이론 검증)

**이론적 특징** (시뮬레이션 검증 진행 중):
- Ring Attractor 기반 위치 기억 및 복귀 (수학적 모델, 검증 중)
- 진동/노이즈 억제 가능성 (이론적, 검증 중)
- 단위 계약 강제 (내부 rad, I/O deg) - 코드 레벨 검증 진행 중

---

**2. 세일즈 가치** (로보틱스 산업 적용)

**핵심 포지셔닝**: 
> **"신경 안정화 보조장치"** - 기존 제어 시스템을 대체하지 않고, 침투하여 효과를 극대화

**산업 응용 분야**:
- 🤖 **산업용 로봇 팔**: 정밀 제어 및 관절 안정화 (시뮬레이션)
- 🤖 **관절 제어**: 인간형 로봇, 정밀 조작 (연구 단계)
- 🤖 **손기술 (Fine Manipulation)**: 미세 부품 조립, 수술 로봇 (향후 검증 필요)
- 🤖 **외란 복귀 (Contact Recovery)**: 접촉 후 원래 자세로 복귀
- 🤖 **미세 진동 억제**: 관절의 미세 진동 안정화

**세일즈 포인트**:
- ✅ **기존 시스템 호환**: PID/MPC와 병행 운영 가능 (침투 전략)
- ✅ **위상 메모리**: 마지막 안정 상태를 기억하여 외란 후 복귀
- ✅ **점진적 도입**: 기존 시스템 변경 없이 플러그인 가능
- ✅ **롤백 가능**: Grid Engine OFF 시 기존 시스템 그대로 동작

**비교 지표** (이론적 목표, 실제 검증 필요):
- 외란 후 복귀 시간: 기존 대비 30% 이상 단축 (목표)
- 위상 오차 (RMS): Ring에 의해 상시 억제 (이론적)
- 진동 감쇠 시간: 노이즈 저항성 향상 (이론적)

**⚠️ 중요**: 위 특징들은 수학적 모델 및 시뮬레이션에서 초기 검증이 진행 중이며, 실제 물리 시스템에서의 성능은 지속적인 벤치마킹 및 검증이 필요합니다. 세일즈 가치는 실제 하드웨어 검증 후 평가됩니다.

**상세 문서**:
- 연구용: `docs/5D_CONCEPT_AND_EQUATIONS.md` - 5D 개념 및 수식
- 세일즈용: `docs/ROBOTICS_APPLICATION.md` - 로보틱스 응용
- 통합 전략: `docs/INTEGRATION_STRATEGY.md` - 침투 전략

---

## 🔄 차원 확장 흐름도

```
2D (평면)
  ↓ + Z축
3D (공간)
  ↓ + W축
4D (고차원)
  ↓ + A, B축 (회전)
5D (CNC급 정밀 움직임 → 로봇 일반 움직임)
```

**확장 원칙**:
- 각 차원은 독립적인 Ring Attractor로 구성
- 직교 결합 (⊗)으로 차원 확장
- 동일한 수학적 구조 (뉴턴 2법칙)
- 위상 공간 Tⁿ = S¹ × S¹ × ... × S¹ (n차원 토러스)

**구성 요소**:
- X, Y, Z 방향 각각 독립적인 Ring Attractor
- 위상(phase) 기반 내부 상태
- 좌표(coordinate) 기반 외부 표현

**물리학적 기초**:
- 뉴턴 2법칙 완전 호환 (위치-속도-가속도 적분)
- 열역학적 안정성 (에너지 최소화)
- 경로 통합 (Path Integration)

**뉴턴 제2법칙과의 연관성**:
- Grid Engine은 **뉴턴 제2법칙 (F = ma)**을 위상 공간에 구현한 물리 기반 제어 엔진입니다.
- 경로 통합(Path Integration)을 통해 뉴턴 역학의 이산화된 형태를 구현합니다.
- **2D**: `v(t+Δt) = v(t) + a(t)·Δt`, `r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²`
- **3D**: `v(t+Δt) = v(t) + a(t)·Δt` (3축), `r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²` (3축)
- **4D**: `v(t+Δt) = v(t) + a(t)·Δt` (4축), `r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²` (4축) ✨ NEW
- **5D**: `v(t+Δt) = v(t) + a(t)·Δt` (5축), `r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²` (5축) ✨ NEW
  - 위치 축: `v_x, v_y, v_z [m/s]`, `a_x, a_y, a_z [m/s²]`
  - 회전 축: `v_a, v_b [deg/s]` (입력) → `[rad/s]` (내부), `α_a, α_b [deg/s²]` (입력) → `[rad/s²]` (내부)
- 상세 설명: [docs/NEWTONS_LAW_CONNECTION.md](docs/NEWTONS_LAW_CONNECTION.md) 참조
- 뉴턴 3법칙 분석: [docs/NEWTONS_3RD_LAW_ANALYSIS.md](docs/NEWTONS_3RD_LAW_ANALYSIS.md) 참조

---

## 🚀 빠른 시작

### 설치

```bash
pip install -r requirements.txt
```

또는 개발 모드로 설치:

```bash
pip install -e .
```

### 기본 사용법

#### 2D Grid Engine

```python
from grid_engine import GridEngine, GridInput

# Grid Engine 초기화
engine = GridEngine(initial_x=0.0, initial_y=0.0)

# 속도 입력으로 이동
inp = GridInput(v_x=1.0, v_y=0.0)
output = engine.step(inp)

print(f"위치: ({output.x:.2f}, {output.y:.2f})")
print(f"위상: ({output.phi_x:.2f}, {output.phi_y:.2f})")
```

#### 3D Grid Engine

```python
from grid_engine.dimensions.dim3d import Grid3DEngine, Grid3DInput

# Grid 3D Engine 초기화
engine_3d = Grid3DEngine(initial_x=0.0, initial_y=0.0, initial_z=0.0)

# 3D 속도 입력으로 이동
inp_3d = Grid3DInput(v_x=1.0, v_y=0.5, v_z=0.3)
output_3d = engine_3d.step(inp_3d)

print(f"위치: ({output_3d.x:.2f}, {output_3d.y:.2f}, {output_3d.z:.2f})")
print(f"위상: ({output_3d.phi_x:.2f}, {output_3d.phi_y:.2f}, {output_3d.phi_z:.2f})")
```

#### 4D Grid Engine ✨ NEW

```python
from grid_engine.dimensions.dim4d import Grid4DEngine, Grid4DInput

# Grid 4D Engine 초기화
engine_4d = Grid4DEngine(initial_x=0.0, initial_y=0.0, initial_z=0.0, initial_w=0.0)

# 4D 속도 입력으로 이동
inp_4d = Grid4DInput(v_x=1.0, v_y=0.5, v_z=0.3, v_w=0.2)
output_4d = engine_4d.step(inp_4d)

print(f"위치: ({output_4d.x:.2f}, {output_4d.y:.2f}, {output_4d.z:.2f}, {output_4d.w:.2f})")
print(f"위상: ({output_4d.phi_x:.2f}, {output_4d.phi_y:.2f}, {output_4d.phi_z:.2f}, {output_4d.phi_w:.2f})")
```

#### 5D Grid Engine (CNC급 정밀 움직임 → 로봇 일반 움직임) ✨ NEW

```python
from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DInput

# Grid 5D Engine 초기화
engine_5d = Grid5DEngine(
    initial_x=0.0, initial_y=0.0, initial_z=0.0,
    initial_theta_a=0.0, initial_theta_b=0.0
)

# 5D 속도 입력으로 이동 (위치 + 회전)
inp_5d = Grid5DInput(
    v_x=1.0, v_y=0.5, v_z=0.3,  # 위치 속도 [m/s]
    v_a=0.5, v_b=0.3  # 회전 각속도 [deg/s] (입력 단위)
)
output_5d = engine_5d.step(inp_5d)

print(f"위치: ({output_5d.x:.2f}, {output_5d.y:.2f}, {output_5d.z:.2f}) m")
print(f"각도: A={output_5d.theta_a:.2f}°, B={output_5d.theta_b:.2f}°")
print(f"위상: ({output_5d.phi_x:.2f}, {output_5d.phi_y:.2f}, {output_5d.phi_z:.2f}, {output_5d.phi_a:.2f}, {output_5d.phi_b:.2f}) rad")
```

---

## 📁 프로젝트 구조

```
grid-engine/
├── grid_engine/              # 핵심 엔진 모듈
│   ├── __init__.py
│   ├── config.py            # 2D 설정
│   ├── config_3d.py         # 3D 설정 ✨ NEW
│   ├── types.py             # 2D 타입
│   ├── types_3d.py          # 3D 타입 ✨ NEW
│   ├── integrator.py        # 2D Semi-implicit Euler
│   ├── integrator_3d.py     # 3D Semi-implicit Euler ✨ NEW
│   ├── grid_engine.py       # GridEngine (2D)
│   ├── grid_3d_engine.py    # Grid3DEngine (3D) ✨ NEW
│   ├── projector.py         # 2D 좌표 투영
│   ├── projector_3d.py      # 3D 좌표 투영 ✨ NEW
│   ├── coupling.py          # 위상 정규화 (공통)
│   ├── energy.py            # 에너지 계산 (2D)
│   └── adapters/
│       ├── ring_adapter.py  # 2D Ring Adapter
│       └── ring_3d_adapter.py  # 3D Ring Adapter ✨ NEW
├── examples/                # 실행 가능한 데모 스크립트
│   ├── run_grid_basic_demo.py      # 2D 기본 데모
│   ├── run_grid_visual_demo.py     # 2D 시각화 데모
│   └── run_grid_3d_basic_demo.py   # 3D 기본 데모 ✨ NEW
│   └── run_grid_3d_visual_demo.py  # 3D 시각화 데모 ✨ NEW
├── benchmarks/              # 벤치마크 스크립트 (검증 중) 🔬 NEW
│   ├── drift_test.py              # 장기 드리프트 억제 테스트
│   ├── phase_coherence_test.py    # 5축 위상 일관성 테스트
│   ├── repeatability_test.py      # 반복 가공 정밀도 테스트
│   └── recovery_test.py           # 외란 복귀 테스트
├── tests/                   # 테스트 스위트
│   ├── test_grid_engine_*.py       # 2D 테스트 (6개)
│   └── test_grid_3d_engine_*.py    # 3D 테스트 (2개) ✨ NEW
├── docs/                    # 기술 문서
│   ├── GRID_ENGINE_SPEC.md
│   ├── 3D_CONCEPT_AND_EQUATIONS.md  # 3D 개념 및 수식 ✨ NEW
│   ├── NEWTONS_3RD_LAW_ANALYSIS.md  # 뉴턴 3법칙 분석 ✨ NEW
│   └── ...
├── README.md                # 이 파일 (한국어 - 메인)
├── README_EN.md             # 영어 버전
├── LICENSE                  # MIT 라이선스
├── setup.py                 # 패키지 설정
├── requirements.txt         # 의존성 (ring-attractor-engine 포함)
├── BLOCKCHAIN_HASH_RECORD.md # 블록체인 해시 기록
├── GPG_SIGNING_GUIDE.md     # GPG 서명 가이드
├── REVENUE_SHARING.md       # 코드 재사용 수익 분배 원칙
└── CHANGELOG.md             # 변경 이력
```

---

## 🎯 주요 기능

### 1. 2D/3D/4D 위치 상태 유지
- **2D**: 내부 상태 위상 벡터 \((\phi_x, \phi_y)\), 외부 표현 좌표 \((x, y)\)
- **3D**: 내부 상태 위상 벡터 \((\phi_x, \phi_y, \phi_z)\), 외부 표현 좌표 \((x, y, z)\)
- **4D**: 내부 상태 위상 벡터 \((\phi_x, \phi_y, \phi_z, \phi_w)\), 외부 표현 좌표 \((x, y, z, w)\) ✨ NEW
- Ring Attractor 기반 안정화 (2D: Ring X ⊗ Ring Y, 3D: Ring X ⊗ Ring Y ⊗ Ring Z, 4D: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W)

### 2. 경로 통합 (Path Integration)
- 속도 벡터 입력 (2D/3D/4D)
- 가속도 벡터 입력 (선택적, 2D/3D/4D)
- 뉴턴 2법칙 완전 호환 (2D/3D/4D)

### 3. 에너지 최소화
- 에너지 함수 기반 안정화
- 열역학적 안정성
- 진단 모드 지원

### 4. 3D 확장 기능
- **3D 경로 통합**: 뉴턴 2법칙 3축 확장
- **3D Ring 안정화**: 3개 Ring Attractor 직교 결합
- **3D 좌표 투영**: 위상 공간 T³ = S¹ × S¹ × S¹
- **3D 시각화**: 나선형 궤적 및 위상 공간 시각화

### 5. 4D 확장 기능 ✨ NEW
- **4D 경로 통합**: 뉴턴 2법칙 4축 확장
- **4D Ring 안정화**: 4개 Ring Attractor 직교 결합
- **4D 좌표 투영**: 위상 공간 T⁴ = S¹ × S¹ × S¹ × S¹
- **4D 시각화**: 4D 궤적 및 위상 공간 시각화 (W축을 색상으로 표현)

---

## 🔬 기술 배경

### Grid = Ring ⊗ Ring (2D)

**구조**:
- X 방향: 독립적인 Ring Attractor
- Y 방향: 독립적인 Ring Attractor
- 직교 결합으로 2D 공간 표현

**수식**:
\[
\phi_x(t+\Delta t) = \phi_x(t) + v_x(t) \cdot \Delta t + \frac{1}{2}a_x(t) \cdot \Delta t^2
\]
\[
\phi_y(t+\Delta t) = \phi_y(t) + v_y(t) \cdot \Delta t + \frac{1}{2}a_y(t) \cdot \Delta t^2
\]

**좌표 변환**:
\[
x = \phi_x \cdot \frac{L_x}{2\pi}, \quad y = \phi_y \cdot \frac{L_y}{2\pi}
\]

### Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z ✨ NEW

**구조**:
- X, Y, Z 방향: 각각 독립적인 Ring Attractor
- 직교 결합으로 3D 공간 표현
- 위상 공간: T³ = S¹ × S¹ × S¹ (토러스, 3차원)

**수식** (3D 확장):
\[
\phi_x(t+\Delta t) = \phi_x(t) + v_x(t) \cdot \Delta t + \frac{1}{2}a_x(t) \cdot \Delta t^2
\]
\[
\phi_y(t+\Delta t) = \phi_y(t) + v_y(t) \cdot \Delta t + \frac{1}{2}a_y(t) \cdot \Delta t^2
\]
\[
\phi_z(t+\Delta t) = \phi_z(t) + v_z(t) \cdot \Delta t + \frac{1}{2}a_z(t) \cdot \Delta t^2
\]

**좌표 변환** (3D):
\[
x = \phi_x \cdot \frac{L_x}{2\pi}, \quad y = \phi_y \cdot \frac{L_y}{2\pi}, \quad z = \phi_z \cdot \frac{L_z}{2\pi}
\]

**상세 설명**: [docs/3D_CONCEPT_AND_EQUATIONS.md](docs/3D_CONCEPT_AND_EQUATIONS.md) 참조

---

## 🔒 단위 계약 (Unit Contract) ⚠️ 중요

Grid Engine은 물리 법칙의 일관성을 유지하기 위해 엄격한 단위 규칙을 따릅니다.

**핵심 규칙**:
- 🔒 **엔진 내부**: 무조건 `rad`, `rad/s`, `rad/s²` (물리 법칙 일관성)
- 🔒 **입력/출력**: `deg`, `deg/s`, `deg/s²` (I/O 편의성)
- 🔒 **변환 지점**: `integrator` (입력), `projector` (출력)

**5D (로봇 관절 제어) 예시**:
```python
# 입력: deg 단위
inp = Grid5DInput(v_a=0.5, v_b=0.3)  # [deg/s]

# 내부: rad 단위 (자동 변환)
# integrator에서: v_a_rad = math.radians(0.5) = 0.0087 [rad/s]

# 출력: deg 단위 (projector에서 변환)
# output.theta_a = math.degrees(phi_a)  # [deg]
```

**상세 설명**: [docs/UNIT_CONTRACT.md](docs/UNIT_CONTRACT.md) 참조

---

## 📚 문서

### 설계 문서
- `docs/GRID_ENGINE_SPEC.md` - 전체 설계 명세서
- `docs/GRID_ENGINE_MINIMAL_EQUATIONS.md` - 최소 수식 세트
- `docs/GRID_ENGINE_THEORETICAL_FOUNDATION.md` - 이론적 기초
- `docs/NEWTONS_LAW_CONNECTION.md` - **뉴턴 제2법칙과의 연관성** (상세 설명)
- `docs/3D_CONCEPT_AND_EQUATIONS.md` - **3D 개념 및 수식**
- `docs/4D_CONCEPT_AND_EQUATIONS.md` - **4D 개념 및 수식** ✨ NEW
- `docs/5D_CONCEPT_AND_EQUATIONS.md` - **5D 개념 및 수식 (CNC급 정밀 움직임)** ✨ NEW
- `docs/ROBOTICS_APPLICATION.md` - **로보틱스 응용 (정밀 운동 제어)** ✨ NEW
- `docs/INTEGRATION_STRATEGY.md` - **통합 전략 (침투 전략)** - ⚠️ 핵심 ✨ NEW
- `docs/NEWTONS_3RD_LAW_ANALYSIS.md` - **뉴턴 3법칙 분석**
- `docs/UNIT_CONTRACT.md` - **단위 계약 (Unit Contract)** - ⚠️ 중요 ✨ NEW
- `docs/FINAL_RESULTS.md` - **벤치마크 초기 결과** (검증 중) 🔬 NEW
- `docs/PROBLEM_ANALYSIS.md` - **문제 분석 및 해결 방법** 🔬 NEW
- `docs/GRID_ENGINE_ARCHITECTURE.md` - **아키텍처 문서** (Reference Stabilizer) 🔬 NEW

### 사용 가이드
- `README.md` (한국어 - 메인)
- `README_EN.md` (영어)

### 예제
- `examples/run_grid_basic_demo.py` - 2D 기본 데모
- `examples/run_grid_visual_demo.py` - 2D 시각화 데모
- `examples/run_grid_3d_basic_demo.py` - 3D 기본 데모
- `examples/run_grid_3d_visual_demo.py` - 3D 시각화 데모 (나선형 궤적)
- `examples/run_grid_4d_basic_demo.py` - 4D 기본 데모 ✨ NEW
- `examples/run_grid_4d_visual_demo.py` - 4D 시각화 데모 (4D 궤적) ✨ NEW
- `examples/run_grid_5d_basic_demo.py` - 5D 기본 데모 (로봇 관절 제어) ✨ NEW
- `examples/run_grid_5d_visual_demo.py` - 5D 시각화 데모 (5D 궤적) ✨ NEW
- `examples/pid_grid_adapter_demo.py` - PID + Grid Engine 통합 예제 (침투 전략) ✨ NEW

---

## 🧪 테스트

### 모든 테스트 실행
```bash
pytest tests/ -v
```

### 특정 테스트 실행
```bash
pytest tests/test_grid_engine_init.py -v
```

---

## 🔬 벤치마크 초기 결과 (검증 중)

⚠️ **주의**: 아래 결과는 초기 검증 결과입니다. 지속적인 테스트와 개선이 진행 중입니다.

### Grid Engine의 역할: Persistent Bias Estimator

Grid Engine은 **Persistent Bias Estimator**로 구현되어 장기 드리프트를 학습하고 보정합니다.

**핵심 개념**:
- **장기 드리프트 (Long-term Drift)**: 시간이 지나면서 누적되는 시스템 편향
  - 예: 열 변형, 백래시, 마모 등으로 인한 점진적 오차 누적
  - PID만으로는 보정이 어려운 저주파 성분
- **Persistent Bias Learning**: 시스템의 지속적인 편향을 학습하여 보정
- **Reference Stabilizer**: 기준점을 안정화하여 드리프트 억제

**구현 내용** (검증 중):
- 장기 드리프트 학습 및 보정 메커니즘
- Reference Stabilizer 아키텍처
- 저주파 드리프트 억제

### 초기 벤치마크 결과

#### 🔬 장기 드리프트 억제 테스트

**파일**: `benchmarks/drift_test.py`

**테스트 시나리오**:
- 10,000 스텝 동안 지속적인 드리프트 주입 (열 변형/백래시 시뮬레이션)
- PID는 적분 항 제한으로 장기 드리프트 보정 능력 제한
- Grid Engine이 학습한 편향을 기준점에 반영하여 드리프트 억제

**초기 결과** (검증 중):
- RMS 오차: **+38.1% 개선** (초기 결과, 추가 검증 필요)
- 최종 오차: **+51.3% 개선** (초기 결과, 추가 검증 필요)
- Drift Slope: **+3393.3% 개선** (초기 결과, 추가 검증 필요)

**의미** (초기 관찰):
- Grid Engine이 장기 드리프트를 학습하고 보정하는 효과가 초기 결과에서 관찰됨
- 다양한 드리프트 패턴과 환경에서의 추가 검증 필요

**초기 판정**: 🔬 **긍정적인 초기 결과** - 추가 검증 및 다양한 시나리오 테스트 필요

#### 🔬 5축 위상 일관성 테스트

**파일**: `benchmarks/phase_coherence_test.py`

**테스트 시나리오**:
- 5개 축이 동시에 움직이는 복합 움직임 시뮬레이션
- 전체 자세의 위상 일관성 측정
- PID는 축별 제어, Grid Engine은 5축 전체 위상 일관성 유지

**초기 결과** (검증 중):
- 위상 일관성 점수: **+67.2% 개선** (초기 결과, 추가 검증 필요)

**의미** (초기 관찰):
- Grid Engine이 다축 동기화에서 긍정적인 효과를 보임
- 다양한 궤적 패턴에서의 추가 검증 필요

**초기 판정**: 🔬 **긍정적인 초기 결과** - 추가 검증 및 다양한 시나리오 테스트 필요

#### ⚠️ 반복 가공 정밀도 테스트

**파일**: `benchmarks/repeatability_test.py`

**테스트 시나리오**:
- 동일 가공을 100회 반복
- 반복 시 정밀도 유지 능력 측정

**초기 결과** (최적화 진행 중):
- 표준 편차: **+6.0% 개선** (제한적, 최적화 진행 중)

**초기 판정**: ⚠️ **제한적인 초기 결과** - 최적화 및 추가 검증 진행 중

### 외란 복귀에 대한 현재 상태

**외란 (Disturbance)의 개념**:
- 시스템에 가해지는 예기치 않은 외부 힘
- 예: 접촉 충격, 진동, 노이즈 등
- 단기적이고 고주파 성분이 주로 포함

**현재 벤치마크 상황**:
- 🔬 **장기 드리프트 억제**: 초기 결과에서 긍정적인 효과 관찰 (검증 중)
- 🔬 **5축 위상 일관성**: 초기 결과에서 긍정적인 효과 관찰 (검증 중)
- ⚠️ **단기 외란 복귀**: `recovery_test.py`는 이전 버전이며, Persistent Bias Estimator 적용 및 검증 필요

**Grid Engine의 강점** (초기 관찰):
- 장기 드리프트 학습 및 보정에 효과적 (초기 결과)
- 다축 동기화에서 긍정적인 효과 (초기 결과)
- 단기 외란 복귀는 추가 검증 필요

### 벤치마크 실행

```bash
# 장기 드리프트 억제 테스트
python3 benchmarks/drift_test.py

# 5축 위상 일관성 테스트
python3 benchmarks/phase_coherence_test.py

# 반복 가공 정밀도 테스트
python3 benchmarks/repeatability_test.py
```

### 관련 문서

- `docs/FINAL_RESULTS.md` - 벤치마크 초기 결과 상세 (검증 중)
- `docs/PROBLEM_ANALYSIS.md` - 문제 분석 및 해결 방법
- `docs/GRID_ENGINE_ARCHITECTURE.md` - 아키텍처 문서
- `benchmarks/` - 벤치마크 스크립트

---

## 💰 코드 재사용 수익 분배

코드 재사용으로 수익이 발생할 경우 분배 원칙은 `REVENUE_SHARING.md`를 참조하세요.

---

## 🔐 블록체인 해시 기록

이 프로젝트는 블록체인 해시 기록을 사용하여:
- 공개 발매 증명
- 파일 무결성 보장
- 기술적 선행 기술 증명

**해시 기록**: `BLOCKCHAIN_HASH_RECORD.md` 참조

---

## 📝 라이선스

**MIT 라이선스** - 자세한 내용은 `LICENSE` 파일 참조

이 기술은 공개적으로 사용 가능하며 (특허 없음) 다음과 같이 사용할 수 있습니다:
- 연구/교육용 자유 사용
- 상업적 사용시 `REVENUE_SHARING.md` 참조

---

## 🔗 관련 레포지토리

### 의존성
- [ring-attractor-engine](https://github.com/qquartsco-svg/ring-attractor-engine) - Ring Attractor Engine (이 엔진이 사용)

### 확장 가능성
- **Context Binder**: 의미 기억 (고차원) - 다음 단계

---

## 📞 문의

**GitHub Issues**: [레포지토리 Issues](https://github.com/qquartsco-svg/grid-engine/issues)

---

**Last Updated**: 2026-01-20  
**Version**: v0.4.0-alpha (5D 확장, 벤치마크 검증 중) 🔬  
**Status**: Alpha (2D/3D/4D/5D 구현 진행 중, 벤치마크 검증 진행 중) 🔬  
**Tag**: v0.4.0-alpha.benchmark-in-progress  
**Author**: GNJz  
**Made in GNJz**

⚠️ **주의**: 이 프로젝트는 지속적으로 검증되고 개선되고 있습니다. 벤치마크 결과는 초기 검증 결과이며, 추가 테스트와 최적화가 진행 중입니다.


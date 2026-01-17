# Grid Engine

**Grid Engine - 2D 공간 상태 메모리 엔진**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](https://github.com/qquartsco-svg/grid-engine)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/qquartsco-svg/grid-engine)

**English**: [README_EN.md](README_EN.md)

---

## 🎯 무엇을 하는가

**Grid Engine**은 Ring ⊗ Ring 구조로 2D 공간 위치 상태를 안정적으로 유지하는 엔진입니다.

**핵심 구조**: Grid = Ring ⊗ Ring (직교 결합)
- X, Y 방향 각각 독립적인 Ring Attractor
- 위상(phase) 기반 내부 상태
- 좌표(coordinate) 기반 외부 표현

**물리학적 기초**:
- 뉴턴 2법칙 완전 호환 (위치-속도-가속도 적분)
- 열역학적 안정성 (에너지 최소화)
- 경로 통합 (Path Integration)

**뉴턴 제2법칙과의 연관성**:
- Grid Engine은 **뉴턴 제2법칙 (F = ma)**을 위상 공간에 구현한 물리 기반 제어 엔진입니다.
- 경로 통합(Path Integration)을 통해 뉴턴 역학의 이산화된 형태를 구현합니다.
- 물리적 일관성 보장: `v(t+Δt) = v(t) + a(t)·Δt` (속도 업데이트), `r(t+Δt) = r(t) + v(t)·Δt + ½a(t)·Δt²` (위치 업데이트)
- 상세 설명: [docs/NEWTONS_LAW_CONNECTION.md](docs/NEWTONS_LAW_CONNECTION.md) 참조

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

---

## 📁 프로젝트 구조

```
grid-engine/
├── grid_engine/              # 핵심 엔진 모듈
│   ├── __init__.py
│   ├── config.py            # 모든 상수/튜닝
│   ├── types.py             # State/Input/Output/Diagnostics
│   ├── integrator.py        # Semi-implicit Euler
│   ├── grid_engine.py       # GridEngine (조립 + step)
│   ├── coupling.py          # Ring ⊗ Ring 결합
│   ├── energy.py            # 에너지 계산 (진단 전용)
│   └── adapters/
│       └── ring_adapter.py  # Ring Engine 어댑터
├── examples/                # 실행 가능한 데모 스크립트
│   └── run_grid_basic_demo.py
├── tests/                   # 테스트 스위트
│   ├── test_grid_engine_init.py
│   ├── test_grid_engine_path_integration.py
│   ├── test_grid_engine_energy_monotonic.py
│   └── test_grid_engine_fail_safe.py
├── docs/                    # 기술 문서
│   ├── GRID_ENGINE_SPEC.md
│   ├── GRID_ENGINE_MINIMAL_EQUATIONS.md
│   └── GRID_ENGINE_THEORETICAL_FOUNDATION.md
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

### 1. 2D 위치 상태 유지
- 내부 상태: 위상 벡터 \((\phi_x, \phi_y)\)
- 외부 표현: 공간 좌표 \((x, y)\)
- Ring Attractor 기반 안정화

### 2. 경로 통합 (Path Integration)
- 속도 벡터 입력
- 가속도 벡터 입력 (선택적)
- 뉴턴 2법칙 완전 호환

### 3. 에너지 최소화
- 에너지 함수 기반 안정화
- 열역학적 안정성
- 진단 모드 지원

---

## 🔬 기술 배경

### Grid = Ring ⊗ Ring

**구조**:
- X 방향: 독립적인 Ring Attractor
- Y 방향: 독립적인 Ring Attractor
- 직교 결합으로 2D 공간 표현

**수식**:
\[
\phi_x(t+\Delta t) = \phi_x(t) + v_x(t) \cdot \Delta t
\]
\[
\phi_y(t+\Delta t) = \phi_y(t) + v_y(t) \cdot \Delta t
\]

**좌표 변환**:
\[
x = \phi_x \cdot \frac{L_x}{2\pi}, \quad y = \phi_y \cdot \frac{L_y}{2\pi}
\]

---

## 📚 문서

### 설계 문서
- `docs/GRID_ENGINE_SPEC.md` - 전체 설계 명세서
- `docs/GRID_ENGINE_MINIMAL_EQUATIONS.md` - 최소 수식 세트
- `docs/GRID_ENGINE_THEORETICAL_FOUNDATION.md` - 이론적 기초
- `docs/NEWTONS_LAW_CONNECTION.md` - **뉴턴 제2법칙과의 연관성** (상세 설명)

### 사용 가이드
- `README.md` (한국어 - 메인)
- `README_EN.md` (영어)

### 예제
- `examples/` - 사용 예제 코드

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
**Version**: v0.1.1  
**Status**: Alpha (제품화 준비 완료) ✅  
**Author**: GNJz  
**Made in GNJz**


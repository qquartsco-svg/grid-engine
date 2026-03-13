# 소뇌 시스템 파일 경로

**Date**: 2026-01-20  
**Version**: v0.5.0-alpha

---

## 📁 소뇌 시스템 폴더

### 절대 경로
```
/Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine/grid_engine/cerebellum
```

### 상대 경로 (프로젝트 루트 기준)
```
grid_engine/cerebellum/
```

---

## 📄 소뇌 시스템 파일

### 1. 소뇌 엔진 (메인 모듈)

**파일명**: `cerebellum_engine.py`

**절대 경로**:
```
/Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine/grid_engine/cerebellum/cerebellum_engine.py
```

**상대 경로**:
```
grid_engine/cerebellum/cerebellum_engine.py
```

**내용**:
- `CerebellumEngine` 클래스
- `CerebellumConfig` 클래스
- `create_cerebellum_engine()` 함수

---

### 2. 소뇌 모듈 초기화 파일

**파일명**: `__init__.py`

**절대 경로**:
```
/Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine/grid_engine/cerebellum/__init__.py
```

**상대 경로**:
```
grid_engine/cerebellum/__init__.py
```

**내용**:
- 모듈 export 정의
- `CerebellumEngine`, `CerebellumConfig`, `create_cerebellum_engine` export

---

## 🚀 실행 파일 (데모)

### 1. 소뇌 데모

**파일명**: `cerebellum_demo.py`

**절대 경로**:
```
/Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine/examples/cerebellum_demo.py
```

**상대 경로**:
```
examples/cerebellum_demo.py
```

**실행 방법**:
```bash
cd /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine
python3 examples/cerebellum_demo.py
```

**내용**:
- 해마-소뇌 통합 예시
- Predictive Feedforward 예시
- Variance 감소 예시

---

## 📋 전체 파일 구조

```
grid-engine/
├── grid_engine/
│   └── cerebellum/                    # 소뇌 시스템 폴더
│       ├── __init__.py               # 모듈 초기화
│       └── cerebellum_engine.py      # 소뇌 엔진 (메인)
│
└── examples/
    └── cerebellum_demo.py            # 소뇌 데모 실행 파일
```

---

## 🔧 사용 방법

### Python에서 import

```python
# 소뇌 엔진 import
from grid_engine.cerebellum import CerebellumEngine, CerebellumConfig, create_cerebellum_engine

# 또는 직접 import
from grid_engine.cerebellum.cerebellum_engine import CerebellumEngine
```

### 실행 파일 실행

```bash
# 프로젝트 루트에서
cd /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine
python3 examples/cerebellum_demo.py
```

---

## 📝 관련 문서

- `docs/CEREBELLUM_DESIGN.md`: 소뇌 설계 문서
- `docs/HIPPOCAMPUS_CEREBELLUM_INTEGRATION.md`: 해마-소뇌 통합 문서

---

**Author**: GNJz  
**Made in**: GNJz  
**License**: MIT License


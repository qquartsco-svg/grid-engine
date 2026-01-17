# 실행 가능한 파일 목록

Grid Engine의 실행 가능한 파일(데모, 테스트) 목록입니다.

**Last Updated**: 2026-01-20  
**Version**: v0.4.0-alpha (5D Extension Complete) ✨  
**Author**: GNJz

---

## 📁 데모 파일 (examples/)

### 2D Grid Engine 데모

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `run_grid_basic_demo.py` | 2D 기본 데모 (텍스트 출력) | `python3 examples/run_grid_basic_demo.py` |
| `run_grid_visual_demo.py` | 2D 시각화 데모 (그래프) | `python3 examples/run_grid_visual_demo.py` |

### 3D Grid Engine 데모

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `run_grid_3d_basic_demo.py` | 3D 기본 데모 (텍스트 출력) | `python3 examples/run_grid_3d_basic_demo.py` |
| `run_grid_3d_visual_demo.py` | 3D 시각화 데모 (3D 그래프) | `python3 examples/run_grid_3d_visual_demo.py` |

### 4D Grid Engine 데모

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `run_grid_4d_basic_demo.py` | 4D 기본 데모 (텍스트 출력) | `python3 examples/run_grid_4d_basic_demo.py` |
| `run_grid_4d_visual_demo.py` | 4D 시각화 데모 (4D 그래프) | `python3 examples/run_grid_4d_visual_demo.py` |

### 5D Grid Engine 데모 (5축 CNC/로보틱스) ✨ NEW

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `run_grid_5d_basic_demo.py` | 5D 기본 데모 (텍스트 출력) | `python3 examples/run_grid_5d_basic_demo.py` |
| `run_grid_5d_visual_demo.py` | 5D 시각화 데모 (5D 그래프) | `python3 examples/run_grid_5d_visual_demo.py` |

### 통합 예제 ✨ NEW

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `pid_grid_adapter_demo.py` | PID + Grid Engine 어댑터 데모 (침투 전략) | `PYTHONPATH=. python3 examples/pid_grid_adapter_demo.py` |

---

## 🧪 테스트 파일 (tests/)

### 2D Grid Engine 테스트

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `test_grid_engine_init.py` | 2D 초기화 테스트 | `pytest tests/test_grid_engine_init.py` |
| `test_grid_engine_path_integration.py` | 2D 경로 통합 테스트 | `pytest tests/test_grid_engine_path_integration.py` |
| `test_grid_engine_boundary.py` | 2D 경계 조건 테스트 | `pytest tests/test_grid_engine_boundary.py` |
| `test_grid_engine_error_handling.py` | 2D 오류 처리 테스트 | `pytest tests/test_grid_engine_error_handling.py` |
| `test_grid_engine_energy_monotonic.py` | 2D 에너지 감소 테스트 | `pytest tests/test_grid_engine_energy_monotonic.py` |
| `test_grid_engine_fail_safe.py` | 2D 안전 장치 테스트 | `pytest tests/test_grid_engine_fail_safe.py` |

### 3D Grid Engine 테스트

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `test_grid_3d_engine_init.py` | 3D 초기화 테스트 | `pytest tests/test_grid_3d_engine_init.py` |
| `test_grid_3d_engine_path_integration.py` | 3D 경로 통합 테스트 | `pytest tests/test_grid_3d_engine_path_integration.py` |

### 4D Grid Engine 테스트

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `test_grid_4d_engine_init.py` | 4D 초기화 테스트 | `pytest tests/test_grid_4d_engine_init.py` |
| `test_grid_4d_engine_path_integration.py` | 4D 경로 통합 테스트 | `pytest tests/test_grid_4d_engine_path_integration.py` |

### 5D Grid Engine 테스트 (5축 CNC/로보틱스) ✨ NEW

| 파일명 | 설명 | 실행 방법 |
|--------|------|-----------|
| `test_grid_5d_engine_init.py` | 5D 초기화 테스트 | `pytest tests/test_grid_5d_engine_init.py` |
| `test_grid_5d_engine_path_integration.py` | 5D 경로 통합 테스트 (단위 변환 포함) | `pytest tests/test_grid_5d_engine_path_integration.py` |

---

## 🚀 빠른 실행 스크립트

### 전체 테스트 실행

```bash
bash RUN_TESTS.sh
```

또는:

```bash
pytest tests/ -v
```

### 전체 데모 실행

```bash
bash RUN_DEMOS.sh
```

또는 개별 실행:

```bash
# 2D 데모
python3 examples/run_grid_basic_demo.py
python3 examples/run_grid_visual_demo.py

# 3D 데모
python3 examples/run_grid_3d_basic_demo.py
python3 examples/run_grid_3d_visual_demo.py
```

---

## 📊 차원별 테스트 실행

### 2D 테스트만 실행

```bash
pytest tests/test_grid_engine_*.py -v
```

### 3D 테스트만 실행

```bash
pytest tests/test_grid_3d_engine_*.py -v
```

### 4D 테스트만 실행

```bash
pytest tests/test_grid_4d_engine_*.py -v
```

---

## 🔍 특정 테스트 실행

### 특정 테스트 함수만 실행

```bash
# 2D 초기화 테스트만
pytest tests/test_grid_engine_init.py::test_grid_engine_default_init -v

# 3D 경로 통합 테스트만
pytest tests/test_grid_3d_engine_path_integration.py::test_grid_3d_engine_uniform_motion -v

# 4D 초기화 테스트만
pytest tests/test_grid_4d_engine_init.py::test_grid_4d_engine_default_init -v
```

---

## 📝 실행 파일 요약

### 데모 파일 (총 6개)

- **2D**: 2개 (`run_grid_basic_demo.py`, `run_grid_visual_demo.py`)
- **3D**: 2개 (`run_grid_3d_basic_demo.py`, `run_grid_3d_visual_demo.py`)
- **4D**: 2개 (TODO: `run_grid_4d_basic_demo.py`, `run_grid_4d_visual_demo.py`)

### 테스트 파일 (총 10개)

- **2D**: 6개 (초기화, 경로 통합, 경계, 오류 처리, 에너지, 안전 장치)
- **3D**: 2개 (초기화, 경로 통합)
- **4D**: 2개 (초기화, 경로 통합)

---

## ⚠️ 주의사항

1. **의존성**: `ring-attractor-engine` 패키지가 설치되어 있어야 합니다.
2. **Python 버전**: Python 3.8 이상 필요
3. **시각화**: 시각화 데모는 `matplotlib` 필요

---

**Author**: GNJz  
**Created**: 2026-01-20  
**Made in GNJz**  
**Version**: v0.3.0-alpha  
**License**: MIT License

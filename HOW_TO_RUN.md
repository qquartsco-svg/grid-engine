# Grid Engine 실행 가이드

## 실행 파일 위치

### 데모 실행 파일

```
examples/
├── run_grid_basic_demo.py      # 기본 데모 (위상/속도 출력)
└── run_grid_visual_demo.py     # 시각화 데모 (그래프 생성)
```

### 테스트 실행 파일

```
tests/
├── test_grid_engine_init.py              # 초기화 테스트
├── test_grid_engine_path_integration.py  # 경로 통합 테스트
├── test_grid_engine_energy_monotonic.py  # 에너지 단조성 테스트
├── test_grid_engine_fail_safe.py         # Fail-safe 테스트
├── test_grid_engine_boundary.py          # 경계 조건 테스트
└── test_grid_engine_error_handling.py    # 오류 처리 테스트
```

## 실행 방법

### 1. 기본 데모 실행

```bash
cd grid-engine
python3 examples/run_grid_basic_demo.py
```

또는:

```bash
cd grid-engine
./RUN_DEMOS.sh basic
```

### 2. 시각화 데모 실행

```bash
cd grid-engine
python3 examples/run_grid_visual_demo.py
```

또는:

```bash
cd grid-engine
./RUN_DEMOS.sh visual
```

**주의**: 시각화 데모는 `matplotlib`이 필요합니다.

```bash
pip install matplotlib
```

### 3. 모든 데모 실행

```bash
cd grid-engine
./RUN_DEMOS.sh all
```

### 4. 테스트 실행

```bash
cd grid-engine
python3 -m pytest tests/ -v
```

또는:

```bash
cd grid-engine
./RUN_TESTS.sh
```

### 5. 특정 테스트만 실행

```bash
cd grid-engine
./RUN_TESTS.sh -k test_name
```

예시:

```bash
./RUN_TESTS.sh -k boundary    # 경계 조건 테스트만
./RUN_TESTS.sh -k init        # 초기화 테스트만
```

## 터미널에서 실행 예시

### 기본 데모

```bash
$ cd /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine
$ python3 examples/run_grid_basic_demo.py

============================================================
Grid Engine 기본 데모
============================================================

📌 참고: Grid Engine은 내부 위상 상태만 유지합니다.
   좌표 투영은 상위 시스템의 책임입니다.
   시각화 데모: examples/run_grid_visual_demo.py

1. Grid Engine 초기화...
...
```

### 시각화 데모

```bash
$ python3 examples/run_grid_visual_demo.py

============================================================
Grid Engine 시각화 데모
============================================================
...
```

### 테스트 실행

```bash
$ ./RUN_TESTS.sh

============================================================
Grid Engine 테스트 실행
============================================================

테스트 디렉토리: tests/
테스트 파일:
  - test_grid_engine_boundary.py
  - test_grid_engine_error_handling.py
  ...

============================== 26 passed in 1.05s ==============================
```

## 실행 스크립트

### RUN_DEMOS.sh

데모 실행 스크립트

```bash
./RUN_DEMOS.sh [basic|visual|all]
```

### RUN_TESTS.sh

테스트 실행 스크립트

```bash
./RUN_TESTS.sh              # 모든 테스트
./RUN_TESTS.sh -v           # 상세 출력
./RUN_TESTS.sh -k test_name # 특정 테스트
```

## 전체 실행 경로

### 현재 작업 디렉토리에서 실행

```bash
# 기본 데모
python3 /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine/examples/run_grid_basic_demo.py

# 시각화 데모
python3 /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine/examples/run_grid_visual_demo.py

# 테스트
cd /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine
./RUN_TESTS.sh
```

### grid-engine 디렉토리에서 실행

```bash
cd /Users/jazzin/Desktop/Hippo_memory/v3_Upgraded/hippo_memory_v3.0.0/release/grid-engine

# 데모
python3 examples/run_grid_basic_demo.py
python3 examples/run_grid_visual_demo.py

# 또는 스크립트 사용
./RUN_DEMOS.sh all

# 테스트
python3 -m pytest tests/ -v
# 또는 스크립트 사용
./RUN_TESTS.sh
```

## 출력 파일

### 시각화 데모 실행 시 생성되는 파일

```
examples/
└── grid_engine_trajectory.png  # 궤적 그래프
```

## 의존성

### 필수 패키지

```bash
pip install numpy
```

### 선택적 패키지

```bash
pip install pytest          # 테스트 실행용
pip install matplotlib      # 시각화 데모용
```

## 문제 해결

### ImportError 발생 시

```bash
# grid-engine 디렉토리에서 실행
cd grid-engine
python3 examples/run_grid_basic_demo.py
```

### pytest가 없는 경우

```bash
pip install pytest
```

### matplotlib이 없는 경우 (시각화 데모)

```bash
pip install matplotlib
```

---

**Author**: [작성자 시그니처]
**Created**: 2026-01

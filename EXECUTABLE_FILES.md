# 실행 파일 위치 가이드

## Grid Engine v0.2.0 (2D + 3D) - 실행 파일 목록

### 데모 실행 파일

#### 1. 2D 기본 데모
**위치**: `examples/run_grid_basic_demo.py`

**실행 방법**:
```bash
cd grid-engine
python3 examples/run_grid_basic_demo.py
```

**기능**:
- Grid Engine 2D 기본 사용법 시연
- 위상 상태 및 속도 변화 출력
- 좌표 투영은 별도 데모 참조

---

#### 2. 2D 시각화 데모
**위치**: `examples/run_grid_visual_demo.py`

**실행 방법**:
```bash
cd grid-engine
python3 examples/run_grid_visual_demo.py
```

**기능**:
- 2D 궤적 시각화
- 위상 변화 그래프
- 속도 변화 그래프
- 위상 공간 궤적
- 출력: `examples/grid_engine_trajectory.png`

---

#### 3. 3D 기본 데모 (NEW)
**위치**: `examples/run_grid_3d_basic_demo.py`

**실행 방법**:
```bash
cd grid-engine
python3 examples/run_grid_3d_basic_demo.py
```

**기능**:
- Grid Engine 3D 기본 사용법 시연
- 3D 위상 상태 및 속도 변화 출력
- Ring X ⊗ Ring Y ⊗ Ring Z 조립 시연
- 3D 경로 통합 (뉴턴 2법칙 3D 확장)

---

### 테스트 실행 파일

#### 1. 전체 테스트 실행
**위치**: `RUN_TESTS.sh`

**실행 방법**:
```bash
cd grid-engine
./RUN_TESTS.sh
```

**기능**:
- 모든 테스트 실행 (2D + 3D)
- pytest를 사용한 자동 테스트
- 테스트 커버리지 확인

---

#### 2. 개별 테스트 파일

**위치**: `tests/`

**2D 테스트 파일**:
- `test_grid_engine_init.py` - 초기화 테스트 (3개)
- `test_grid_engine_path_integration.py` - 경로 적분 테스트 (2개)
- `test_grid_engine_energy_monotonic.py` - 에너지 테스트 (1개)
- `test_grid_engine_fail_safe.py` - 안전장치 테스트 (2개)
- `test_grid_engine_boundary.py` - 경계 조건 테스트 (6개)
- `test_grid_engine_error_handling.py` - 오류 처리 테스트 (12개)

**3D 테스트 파일 (NEW)**:
- `test_grid_3d_engine_init.py` - 3D 초기화 테스트 (5개)
- `test_grid_3d_engine_path_integration.py` - 3D 경로 적분 테스트 (4개)

**총 테스트 수**: 26개 (2D) + 9개 (3D) = 35개

**실행 방법**:
```bash
# 전체 테스트
pytest tests/

# 2D 테스트만
pytest tests/test_grid_engine_*.py

# 3D 테스트만
pytest tests/test_grid_3d_engine_*.py

# 특정 테스트 파일
pytest tests/test_grid_3d_engine_init.py

# 특정 테스트 함수
pytest tests/test_grid_3d_engine_init.py::test_grid_3d_engine_default_init
```

---

### 데모 일괄 실행

**위치**: `RUN_DEMOS.sh`

**실행 방법**:
```bash
cd grid-engine
./RUN_DEMOS.sh
```

**기능**:
- 모든 데모 일괄 실행
- 2D 기본 데모 + 2D 시각화 데모 + 3D 기본 데모

---

### Python 패키지 설치

**위치**: `setup.py`

**설치 방법**:
```bash
cd grid-engine

# 개발 모드 설치
pip install -e .

# 또는 의존성만 설치
pip install -r requirements.txt
```

**설치 후 사용**:
```python
# 2D 사용
from grid_engine import GridEngine, GridInput

engine = GridEngine()
inp = GridInput(v_x=1.0, v_y=0.0)
output = engine.step(inp)

# 3D 사용 (NEW)
from grid_engine.grid_3d_engine import Grid3DEngine
from grid_engine.types_3d import Grid3DInput

engine_3d = Grid3DEngine()
inp_3d = Grid3DInput(v_x=1.0, v_y=0.5, v_z=0.3)
output_3d = engine_3d.step(inp_3d)
```

---

## 실행 파일 위치 요약

```
grid-engine/
├── examples/                          # 데모 파일
│   ├── run_grid_basic_demo.py        # 2D 기본 데모
│   ├── run_grid_visual_demo.py       # 2D 시각화 데모
│   ├── run_grid_3d_basic_demo.py    # 3D 기본 데모 (NEW)
│   └── grid_engine_trajectory.png    # 시각화 출력 (실행 후 생성)
│
├── tests/                             # 테스트 파일
│   ├── test_grid_engine_*.py         # 2D 테스트 (6개 파일)
│   ├── test_grid_3d_engine_*.py     # 3D 테스트 (2개 파일) (NEW)
│   └── ...
│
├── grid_engine/                        # 핵심 모듈
│   ├── grid_engine.py                # 2D Grid Engine
│   ├── grid_3d_engine.py             # 3D Grid Engine (NEW)
│   ├── types.py                      # 2D 타입
│   ├── types_3d.py                   # 3D 타입 (NEW)
│   ├── config.py                     # 2D 설정
│   ├── config_3d.py                  # 3D 설정 (NEW)
│   ├── integrator.py                 # 2D 적분기
│   ├── integrator_3d.py              # 3D 적분기 (NEW)
│   ├── projector.py                  # 2D 좌표 투영
│   ├── projector_3d.py                # 3D 좌표 투영 (NEW)
│   ├── adapters/
│   │   ├── ring_adapter.py           # 2D Ring Adapter
│   │   └── ring_3d_adapter.py       # 3D Ring Adapter (NEW)
│   └── ...
│
├── RUN_TESTS.sh                       # 테스트 실행 스크립트
├── RUN_DEMOS.sh                       # 데모 실행 스크립트
│
├── setup.py                           # 패키지 설치 파일
└── requirements.txt                   # 의존성 목록
```

---

## 빠른 시작 가이드

### 1. 첫 실행 (2D 기본 데모)
```bash
cd grid-engine
python3 examples/run_grid_basic_demo.py
```

### 2. 3D 데모 실행 (NEW)
```bash
cd grid-engine
python3 examples/run_grid_3d_basic_demo.py
```

### 3. 2D 시각화 데모
```bash
cd grid-engine
python3 examples/run_grid_visual_demo.py
```

### 4. 테스트 실행
```bash
cd grid-engine
./RUN_TESTS.sh
```

### 5. 전체 검증
```bash
cd grid-engine
./RUN_DEMOS.sh && ./RUN_TESTS.sh
```

---

## 버전별 기능

### v0.1.1 (2D Grid Engine)
- ✅ 2D 경로 통합 (뉴턴 2법칙)
- ✅ Ring X ⊗ Ring Y 조립
- ✅ 2D 좌표 투영
- ✅ 2D 테스트 (26개)

### v0.2.0 (3D Grid Engine) (NEW)
- ✅ 3D 경로 통합 (뉴턴 2법칙 3D 확장)
- ✅ Ring X ⊗ Ring Y ⊗ Ring Z 조립
- ✅ 3D 좌표 투영
- ✅ 3D 테스트 (9개)

---

## 주의사항

1. **의존성 설치 필수**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ring Engine 의존성**:
   - `ring-attractor-engine>=1.0.0` 필요
   - 상위 디렉토리에 설치되어 있어야 함

3. **Python 버전**:
   - Python 3.8 이상 필요

4. **시각화 데모**:
   - matplotlib 필요 (`pip install matplotlib`)
   - 실행 후 `examples/grid_engine_trajectory.png` 생성

5. **3D 기능**:
   - 3D Grid Engine은 2D를 확장한 버전
   - 모든 2D 기능이 3D로 확장됨

---

**Author**: GNJz
**Created**: 2026-01-20
**Updated**: 2026-01-20 (3D 확장 추가)
**Version**: v0.2.0
**Made in GNJz**

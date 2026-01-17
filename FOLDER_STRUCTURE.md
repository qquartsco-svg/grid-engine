# Grid Engine 폴더 구조

## 전체 구조

```
grid-engine/
├── grid_engine/              # 핵심 모듈
│   ├── __init__.py
│   ├── grid_engine.py        # 2D Grid Engine
│   ├── grid_3d_engine.py    # 3D Grid Engine (NEW)
│   ├── types.py             # 2D 타입 정의
│   ├── types_3d.py          # 3D 타입 정의 (NEW)
│   ├── config.py            # 2D 설정
│   ├── config_3d.py         # 3D 설정 (NEW)
│   ├── integrator.py        # 2D 적분기
│   ├── integrator_3d.py     # 3D 적분기 (NEW)
│   ├── projector.py         # 2D 좌표 투영
│   ├── projector_3d.py      # 3D 좌표 투영 (NEW)
│   ├── coupling.py          # 위상 정규화 (공통)
│   ├── energy.py            # 에너지 계산 (2D)
│   └── adapters/            # Ring Adapter
│       ├── __init__.py
│       ├── ring_adapter.py  # 2D Ring Adapter
│       └── ring_3d_adapter.py  # 3D Ring Adapter (NEW)
│
├── examples/                 # 데모 파일
│   ├── run_grid_basic_demo.py      # 2D 기본 데모
│   ├── run_grid_visual_demo.py     # 2D 시각화 데모
│   └── run_grid_3d_basic_demo.py   # 3D 기본 데모 (NEW)
│
├── tests/                    # 테스트 파일
│   ├── test_grid_engine_*.py       # 2D 테스트 (6개)
│   └── test_grid_3d_engine_*.py    # 3D 테스트 (2개) (NEW)
│
├── docs/                     # 문서
│   ├── GRID_ENGINE_SPEC.md
│   ├── 3D_CONCEPT_AND_EQUATIONS.md  # 3D 개념 및 수식 (NEW)
│   ├── NEWTONS_LAW_CONNECTION.md
│   ├── NEWTONS_3RD_LAW_ANALYSIS.md  # 뉴턴 3법칙 분석 (NEW)
│   └── ...
│
├── RUN_TESTS.sh              # 테스트 실행 스크립트
├── RUN_DEMOS.sh              # 데모 실행 스크립트
├── EXECUTABLE_FILES.md       # 실행 파일 가이드
├── FOLDER_STRUCTURE.md       # 이 파일
├── setup.py                  # 패키지 설정
├── requirements.txt          # 의존성
└── README.md                 # 메인 문서
```

## 모듈 설명

### 2D 모듈
- `grid_engine.py`: 2D Grid Engine 메인 클래스
- `types.py`: GridState, GridInput, GridOutput (2D)
- `config.py`: GridEngineConfig (2D)
- `integrator.py`: 2D 경로 통합 (뉴턴 2법칙)
- `projector.py`: 2D 좌표 투영

### 3D 모듈 (NEW)
- `grid_3d_engine.py`: 3D Grid Engine 메인 클래스
- `types_3d.py`: Grid3DState, Grid3DInput, Grid3DOutput (3D)
- `config_3d.py`: Grid3DConfig (3D)
- `integrator_3d.py`: 3D 경로 통합 (뉴턴 2법칙 3D 확장)
- `projector_3d.py`: 3D 좌표 투영

### 공통 모듈
- `coupling.py`: 위상 정규화 (2D/3D 공통)
- `energy.py`: 에너지 계산 (현재 2D만 지원)

### Adapter 모듈
- `ring_adapter.py`: Ring X ⊗ Ring Y (2D)
- `ring_3d_adapter.py`: Ring X ⊗ Ring Y ⊗ Ring Z (3D)

## 파일 크기 요약

```
grid-engine/
├── grid_engine/              ~50KB (2D + 3D)
├── examples/                 ~15KB
├── tests/                    ~25KB
└── docs/                     ~100KB
```

## 버전 정보

- **v0.1.1**: 2D Grid Engine 완성
- **v0.2.0**: 3D Grid Engine 추가 (NEW)

Author: GNJz
Created: 2026-01-20
Updated: 2026-01-20 (3D 확장 추가)
Version: v0.2.0
Made in GNJz

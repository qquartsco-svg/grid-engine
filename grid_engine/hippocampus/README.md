# Hippocampus Module

**해마(Hippocampus) 구조 - 공간 기반 기억 시스템**

**Version**: v0.4.0-alpha  
**Status**: ✅ **COMPLETED**  
**Date**: 2026-01-20

---

## 📋 개요

이 모듈은 Grid Engine의 해마(Hippocampus) 계층을 구현합니다. 해마는 생물학적 뇌 구조에서 공간 기억과 장기 기억을 담당하는 기관입니다.

**핵심 역할**: 장기적 항상성과 맥락적 안정을 제공하는 공간 기반 기억 시스템

---

## 🧠 구성 요소

### 1. Place Cells (`place_cells.py`)
- **역할**: 장소별 독립적인 기억(bias) 저장
- **기능**: 위상 해싱을 통한 공간 분리, 장소별 독립적인 bias 저장
- **클래스**: `PlaceMemory`, `PlaceCellManager`

### 2. Context Binder (`context_binder.py`)
- **역할**: 맥락별 기억 분리
- **기능**: Place + Context 조합으로 기억 분리, 동일 장소에서도 맥락별 독립 기억
- **클래스**: `ContextMemory`, `ContextBinder`

### 3. Learning Gate (`learning_gate.py`)
- **역할**: 학습 조건 제어
- **기능**: 학습 조건 명시적 제어, 노이즈 학습 방지
- **클래스**: `LearningGateConfig`, `LearningGate`

### 4. Replay/Consolidation (`replay_consolidation.py`)
- **역할**: 기억 정제 및 장기 기억 고정
- **기능**: 휴지기에 기억 재검토, 통계적 유의성 검증을 통한 장기 기억 고정
- **클래스**: `PlaceMemoryWithHistory`, `ReplayConsolidation`, `ReplayConsolidationManager`

### 5. Replay Buffer (`replay_buffer.py`)
- **역할**: 안정 구간 추출을 위한 버퍼
- **기능**: Online phase에서 trajectory/error/state 기록, Replay phase에서 안정 구간 추출
- **클래스**: `ReplayBufferPoint`, `ReplayBuffer`

---

## 📊 벤치마크 검증 결과

### ✅ 성공 사례

1. **장기 드리프트 억제** (repeatability_test.py)
   - Persistent Bias: **+51.3% 개선** (drift slope 감소)

2. **Place/Replay 재방문 효과** (place_context_revisit_test.py)
   - Place(+Replay): **+5.9% 개선** (PID 대비)

---

## 🔗 통합

이 모듈은 `Grid5DEngine`에서 통합되어 사용됩니다:

```python
from grid_engine.hippocampus import (
    PlaceCellManager,
    ContextBinder,
    LearningGate,
    ReplayConsolidation,
    ReplayBuffer
)
```

---

## 📝 상세 문서

- [해마 구조 완성 선언](../../docs/HIPPOCAMPUS_COMPLETION.md)

---

**Author**: GNJz  
**Made in**: GNJz  
**License**: MIT License


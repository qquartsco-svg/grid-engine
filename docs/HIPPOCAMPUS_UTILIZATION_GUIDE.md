# 해마 메모리 활용 가이드

**Date**: 2026-01-20  
**Version**: v0.4.0-alpha  
**Status**: 기능적 완성

---

## 🎯 핵심 질문

**"해마 메모리라는 기억이 형성되는 알고리즘 코드가 구현이 되었는데, 이게 단일 기능으로서 어디에든 붙어서 사용될 수 없다고?"**

**답**: **아니요, 가능합니다!**

**해마 메모리를 범용 모듈로 재정의하여 어떤 시스템에도 붙일 수 있게 만들었습니다.**

---

## 💡 해마 메모리의 본질

### 해마 메모리가 하는 일

**해마 메모리는 "시간에 걸쳐 누적되는 상태 편향을 맥락·장소 단위로 분리 저장하고, 필요할 때 다시 주입할 수 있는 기억 시스템"입니다.**

**즉**:
- ✅ 상태/경향/습관을 기억
- ✅ 시간에 걸친 누적 편향 학습
- ✅ 맥락별 기억 분리
- ✅ 기억 정제 (Replay/Consolidation)

---

## 🔧 범용 인터페이스: UniversalMemory

### 기본 사용법

```python
from grid_engine.hippocampus import UniversalMemory, create_universal_memory

# 범용 메모리 생성
memory = create_universal_memory(memory_dim=5)

# 기억 저장 (RAG의 문서 저장과 유사)
memory.store(
    key=state_vector,  # 상태 벡터
    value=bias_vector,  # 편향/경향
    context={"user": "user_123", "tool": "tool_A"}
)

# 기억 검색 (RAG의 문서 검색과 유사)
memories = memory.retrieve(
    query=query_state,  # 쿼리 상태
    context={"user": "user_123"}
)

# 기억 증강 (RAG의 컨텍스트 제공과 유사)
augmented_context = memory.augment(
    query=query_state,
    context={"user": "user_123"}
)
```

---

## 📦 활용 예시

### 예시 1: LLM에 붙이기

```python
from grid_engine.hippocampus import create_universal_memory
import numpy as np

# 범용 메모리 생성
memory = create_universal_memory(memory_dim=5)

# 대화 상태를 상태 벡터로 저장
conversation_state = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
user_behavior = np.array([0.01, 0.02, 0.0, 0.0, 0.0])  # 사용자가 항상 조금 느리게 반응

# 기억 저장
memory.store(
    key=conversation_state,
    value=user_behavior,
    context={"user": "user_123", "session": "session_1", "time": "morning"}
)

# LLM 쿼리
query = "이 사용자에게 어떻게 대응해야 할까?"
query_state = conversation_state.copy()

# 기억 검색 및 증강
augmented_context = memory.augment(query_state, context={"user": "user_123"})

# LLM이 사용할 수 있는 컨텍스트
llm_context = {
    "user_tendency": "이 사용자는 항상 조금 느리게 반응하는 경향이 있습니다.",
    "recommendation": "천천히 설명하는 것이 좋습니다.",
    "memories": augmented_context["memories"]
}

# LLM에 제공
llm_response = llm.generate(query, context=llm_context)
```

**특징**:
- RAG는 "지난번에 뭐라고 했지?" (명시적 지식)
- 해마는 "이 사용자는 항상 조금 느리게 반응한다" (암묵적 경향)
- 결합: 더 자연스러운 대화

---

### 예시 2: 제어 시스템에 붙이기

```python
from grid_engine.hippocampus import create_universal_memory
import numpy as np

# 범용 메모리 생성
memory = create_universal_memory(memory_dim=5)

# 제어 위치별 편향 저장
position_1 = np.array([1.0, 0.5, 0.3, 10.0, 5.0])
bias_1 = np.array([0.001, 0.002, 0.0, 0.0, 0.0])  # 열 변형으로 인한 편향

# 기억 저장
memory.store(
    key=position_1,
    value=bias_1,
    context={"tool": "tool_A", "temperature": 25.0, "material": "aluminum"}
)

# 제어 쿼리
query_position = position_1.copy()

# 기억 검색
memories = memory.retrieve(query_position, context={"tool": "tool_A"})

# 제어 시스템이 사용할 수 있는 보정값
correction = -memories[0]['bias']
corrected_target = target + correction
```

**특징**:
- 위치별 편향 기억
- 맥락별 편향 분리 (공구별, 온도별)
- 장기 드리프트 억제

---

### 예시 3: 추천 시스템에 붙이기

```python
from grid_engine.hippocampus import create_universal_memory
import numpy as np

# 범용 메모리 생성
memory = create_universal_memory(memory_dim=5)

# 사용자 행동 패턴 저장
user_state = np.array([0.5, 0.3, 0.2, 0.1, 0.0])
user_preference = np.array([0.1, 0.2, 0.0, 0.0, 0.0])  # 사용자가 항상 이런 경향

# 기억 저장
memory.store(
    key=user_state,
    value=user_preference,
    context={"user": "user_456", "time": "evening", "device": "mobile"}
)

# 추천 쿼리
query_state = user_state.copy()

# 기억 검색 및 증강
augmented_context = memory.augment(query_state, context={"user": "user_456"})

# 추천 시스템이 사용할 수 있는 정보
recommendation_context = {
    "user_tendency": "이 사용자는 저녁 시간대에 모바일에서 이런 경향을 보입니다.",
    "recommendation": "비슷한 패턴의 콘텐츠를 추천하세요.",
    "memories": augmented_context["memories"]
}
```

**특징**:
- 사용자 행동 패턴 기억
- 시간대별, 디바이스별 맥락 분리
- 개인화 추천

---

### 예시 4: 게임 AI에 붙이기

```python
from grid_engine.hippocampus import create_universal_memory
import numpy as np

# 범용 메모리 생성
memory = create_universal_memory(memory_dim=5)

# NPC 위치별 행동 패턴 저장
npc_position = np.array([10.0, 5.0, 2.0, 0.0, 0.0])
npc_behavior = np.array([0.05, 0.0, 0.0, 0.0, 0.0])  # 이 위치에서 항상 조금 이렇게 행동

# 기억 저장
memory.store(
    key=npc_position,
    value=npc_behavior,
    context={"npc": "npc_001", "map": "forest", "time": "day"}
)

# 게임 쿼리
query_position = npc_position.copy()

# 기억 검색
memories = memory.retrieve(query_position, context={"npc": "npc_001"})

# 게임 AI가 사용할 수 있는 행동 보정
behavior_correction = memories[0]['bias']
npc_behavior = base_behavior + behavior_correction
```

**특징**:
- 위치별 행동 패턴 기억
- 맵별, 시간대별 맥락 분리
- 자연스러운 NPC 행동

---

### 예시 5: 쿠키브레인에 붙이기

```python
from grid_engine.hippocampus import create_universal_memory
import numpy as np

# 범용 메모리 생성
memory = create_universal_memory(memory_dim=5)

# 에이전트 상태 저장
agent_state = np.array([0.3, 0.2, 0.1, 0.0, 0.0])
agent_tendency = np.array([0.01, 0.0, 0.0, 0.0, 0.0])  # 에이전트가 항상 조금 이렇게 행동

# 기억 저장
memory.store(
    key=agent_state,
    value=agent_tendency,
    context={"agent": "agent_001", "task": "task_A", "environment": "env_1"}
)

# 에이전트 쿼리
query_state = agent_state.copy()

# 기억 검색 및 증강
augmented_context = memory.augment(query_state, context={"agent": "agent_001"})

# 에이전트가 사용할 수 있는 정보
agent_context = {
    "tendency": "이 에이전트는 이 상황에서 항상 조금 이렇게 행동하는 경향이 있습니다.",
    "memories": augmented_context["memories"]
}
```

**특징**:
- 에이전트 상태/습관 기억
- 작업별, 환경별 맥락 분리
- 개성 있는 에이전트

---

## 🔍 해마 메모리 vs RAG 비교

### RAG (Retrieval-Augmented Generation)

**저장**: 텍스트 문서
**검색**: 유사도 검색
**결과**: 답변 (가시적)
**한계**: 시간/상태 개념 없음

### 해마 메모리

**저장**: 상태/경향/습관
**검색**: 공간/맥락 검색
**결과**: 기준점 보정 (비가시적)
**장점**: 시간/상태 개념 있음

### 하이브리드 (권장)

**RAG**: 명시적 지식 (텍스트)
**해마**: 암묵적 경향 (상태)
**결합**: 더 자연스러운 시스템

---

## 🎯 활용 가능 분야

### ✅ 가능한 분야

1. **LLM 애플리케이션**
   - 사용자 행동 패턴 기억
   - 대화 맥락 기억
   - 개인화 대화

2. **제어 시스템**
   - 위치별 편향 기억
   - 맥락별 편향 분리
   - 장기 드리프트 억제

3. **추천 시스템**
   - 사용자 선호도 기억
   - 시간대별, 디바이스별 맥락 분리
   - 개인화 추천

4. **게임 AI**
   - NPC 행동 패턴 기억
   - 맵별, 시간대별 맥락 분리
   - 자연스러운 NPC 행동

5. **에이전트 시스템**
   - 에이전트 상태/습관 기억
   - 작업별, 환경별 맥락 분리
   - 개성 있는 에이전트

6. **시뮬레이터**
   - 상태 기억
   - 반복 시나리오 기억
   - 자연스러운 시뮬레이션

---

## 📋 API 레퍼런스

### UniversalMemory 클래스

#### `store(key, value, context=None, timestamp=None)`
기억 저장

**Parameters**:
- `key`: 기억 키 (위상 벡터, 상태 벡터, 또는 해시 가능한 값)
- `value`: 기억 값 (bias, 경향, 습관 등)
- `context`: 맥락 정보 (도메인 독립적)
- `timestamp`: 타임스탬프 (None이면 현재 시간)

#### `retrieve(query, context=None, top_k=5)`
기억 검색

**Parameters**:
- `query`: 검색 쿼리 (위상 벡터, 상태 벡터, 또는 해시 가능한 값)
- `context`: 맥락 정보
- `top_k`: 상위 K개 기억 반환

**Returns**: 기억 리스트 (각 기억은 Dict 형태)

#### `augment(query, context=None)`
기억 증강

**Parameters**:
- `query`: 검색 쿼리
- `context`: 맥락 정보

**Returns**: 증강된 컨텍스트 (Dict 형태)

#### `replay(current_time=None)`
Replay 수행 (기억 정제)

**Parameters**:
- `current_time`: 현재 시간 (None이면 자동 계산)

**Returns**: Replay 결과 통계

---

## 🚀 다음 단계

### 단계 1: 범용 인터페이스 완성 ✅
- UniversalMemory 클래스 구현 완료
- 기본 API 정의 완료

### 단계 2: 도메인 어댑터 구현 (진행 중)
- LLM 어댑터
- 제어 시스템 어댑터
- 추천 시스템 어댑터

### 단계 3: 제품화
- 문서화
- 마케팅 자료
- 케이스 스터디

---

## 💡 핵심 인사이트

### 해마 메모리의 활용 가능성

**해마 메모리는**:
- ✅ **어디에든 붙일 수 있음** (범용 인터페이스)
- ✅ **일반 AI 기술에 적용 가능** (RAG 스타일)
- ✅ **단일 기능으로서 사용 가능** (UniversalMemory)

**하지만**:
- ⚠️ 소뇌와 결합하면 더 강력함
- ⚠️ 쿠키브레인 부품으로도 사용 가능
- ⚠️ 단독 완제품보다는 모듈/SDK로 적합

---

## 📝 최종 결론

### 질문: "해마 메모리라는 기억이 형성되는 알고리즘 코드가 구현이 되었는데, 이게 단일 기능으로서 어디에든 붙어서 사용될 수 없다고?"

**답**: **아니요, 가능합니다!**

**해결책**:
- ✅ 범용 인터페이스 제공 (UniversalMemory)
- ✅ RAG 스타일 API (store, retrieve, augment)
- ✅ 어떤 시스템에도 붙일 수 있음

**활용 분야**:
- LLM 애플리케이션
- 제어 시스템
- 추천 시스템
- 게임 AI
- 에이전트 시스템
- 시뮬레이터

**결론**: 해마 메모리는 **"어디에든 붙일 수 있는 범용 기억 모듈"**입니다!

---

**Author**: GNJz  
**Made in**: GNJz  
**License**: MIT License


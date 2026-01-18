# 해마 완성 로드맵 (Hippocampus Completion Roadmap)

**Version**: v0.4.0-alpha  
**Author**: GNJz  
**Created**: 2026-01-20  
**Made in GNJz**

---

## 🎯 핵심 원칙

### ❌ 소뇌를 먼저 만들면 안 된다

**이유**:
- 소뇌는 "이미 형성된 상태·기억을 바탕으로 다음 순간을 예측하고 보정하는 기관"
- 현재 상태에서 소뇌를 만들면:
  - 기억 없음 → 예측 불가
  - 상태 의미 없음 → 보정 불가
  - 결과: "빠른데 뭐가 맞는지 모르는 시스템"
  - 결과: 고속 노이즈 증폭기

### ✅ 해마를 먼저 완성해야 한다 (무조건)

**생물학적 발달 순서**:
1. 해마 (공간 + 기억 형성)
2. 피질과의 연결 (의미, 맥락)
3. 소뇌 (미세 조정, 순발력)

**소뇌의 전제 조건**:
- 어디에 있는지 (Place) - 이미 알고 있어야 함
- 지금 상황이 뭔지 (Context) - 이미 알고 있어야 함
- 과거에 뭐가 안정이었는지 (Memory) - 이미 알고 있어야 함

---

## 📊 현재 상태 정확한 정의

### ✅ 완성된 계층: 공간 표현 계층 (Spatial Representation Layer)

- **Grid Cells (Ring Attractor)** → 공간 표현
- **Path Integration** → 자기 위치 추적
- **Persistent Bias** → 장기 안정화

### ❌ 미완성 계층: 기억 통합 계층 (Memory Integration Layer)

- **Place Cells** → 없음
- **Context Binder** → 없음
- **Replay/Consolidation** → 없음

**현재 상태**: "지도는 있는데 기억은 없는 해마"

**정확한 이름**:
- ❌ "지능형 제어 엔진"
- ✅ "고차원 공간 메모리 엔진 (Spatial Memory Core)"

---

## 🚀 다음 단계 작업 계획 (순서 고정)

### ✅ 1단계: Place Cells (가장 중요)

#### 목적

- **Grid는 '좌표계'**: 연속적인 위상 공간 표현
- **Place는 '장소 ID'**: 특정 위치를 고유하게 식별
- 반복 가공이 기억되도록
- 회차 간 학습이 가능하도록

#### 현재 문제점

현재 `Grid5DEngine`의 `bias_estimate`는 **전역 단일 벡터**입니다:
```python
self.bias_estimate: np.ndarray = np.zeros(5)  # 전역 단일 벡터
```

이로 인해:
- 1회차 가공의 열 변형 데이터와 2회차 가공의 백래시 데이터가 하나의 `bias_estimate`에 뒤섞임
- 반복 가공 시 동일 지점의 편향을 불러올 수 없음
- 장소별 독립적인 bias 학습 불가능

#### 구현 방향

1. **Grid 활성 패턴 → 클러스터링**
   - 7D 위상 공간 $\Phi = (\phi_x, \phi_y, \phi_z, \phi_a, \phi_b, \phi_c, \phi_d)$의 특정 조합이 활성화될 때 'Place Cell $i$' 발화
   - 위상 공간을 영역으로 분할 (Place Field)

2. **특정 위상 조합 → Place ID**
   - 위상 벡터를 해시하거나 클러스터링하여 Place ID 생성
   - 예: `place_id = hash(phi_x, phi_y, phi_z, phi_a, phi_b) % num_places`

3. **안정 상태 스냅샷 저장**
   - 각 Place ID마다 독립적인 `bias_estimate` 저장
   - Place별로 안정 상태 스냅샷 저장

#### 구현 구조

```python
class PlaceCellManager:
    def __init__(self, num_places: int = 1000):
        self.place_memory: Dict[int, PlaceMemory] = {}
        # Place ID → PlaceMemory 매핑
    
    def get_place_id(self, phase_vector: np.ndarray) -> int:
        """위상 벡터를 Place ID로 변환"""
        # 위상 공간을 해시하거나 클러스터링
        pass
    
    def get_bias_estimate(self, place_id: int) -> np.ndarray:
        """Place별 bias 추정값 반환"""
        if place_id not in self.place_memory:
            return np.zeros(5)  # 초기값
        return self.place_memory[place_id].bias_estimate
    
    def update_bias_estimate(self, place_id: int, bias: np.ndarray):
        """Place별 bias 업데이트"""
        if place_id not in self.place_memory:
            self.place_memory[place_id] = PlaceMemory()
        self.place_memory[place_id].update_bias(bias)

@dataclass
class PlaceMemory:
    place_id: int
    bias_estimate: np.ndarray = field(default_factory=lambda: np.zeros(5))
    visit_count: int = 0
    last_visit_time: float = 0.0
    stable_state_snapshot: Optional[Grid5DState] = None
```

#### 기대 효과

- 반복 가공 시 동일 지점의 편향 불러오기
- 장소별 독립적인 bias_estimate 할당
- 회차 간 학습 가능

---

### ✅ 2단계: Context Binder

#### 목적

같은 장소라도:
- 공구 다름
- 온도 다름
- 작업 단계 다름

이걸 분리하여 **기억 오염 방지**

#### 현재 문제점

현재 반복 가공 정밀도가 악화(-8.0%)된 원인:
- 1회차 가공의 열 변형 데이터와 2회차 가공의 백래시 데이터가 하나의 `bias_estimate`에 뒤섞임
- Context가 분리되지 않아 Bias 학습이 서로 오염됨

#### 구현 방향

1. **Place + Context 조합으로 기억 분리**
   - `(place_id, context_id)` 조합으로 독립적인 bias 저장
   - 예: `memory_key = (place_id, tool_id, temperature_range, step_id)`

2. **Context별 독립적인 bias_estimate**
   - 각 Context 조합마다 독립적인 `bias_estimate` 할당

3. **외부 상태를 Context로 매핑**
   - 온도, 공구, 작업 단계 등을 Context로 변환
   - 예: `context_id = hash(tool_type, temperature, step_number)`

#### 구현 구조

```python
class ContextBinder:
    def __init__(self):
        self.context_memory: Dict[Tuple[int, int], ContextMemory] = {}
        # (place_id, context_id) → ContextMemory 매핑
    
    def get_context_id(self, external_state: Dict[str, Any]) -> int:
        """외부 상태를 Context ID로 변환"""
        # 온도, 공구, 작업 단계 등을 해시
        context_hash = hash(
            external_state.get('tool_type', 'default'),
            external_state.get('temperature', 20.0),
            external_state.get('step_number', 0)
        )
        return context_hash % 10000  # Context ID
    
    def get_bias_estimate(self, place_id: int, context_id: int) -> np.ndarray:
        """Place + Context 조합의 bias 추정값 반환"""
        key = (place_id, context_id)
        if key not in self.context_memory:
            return np.zeros(5)  # 초기값
        return self.context_memory[key].bias_estimate
    
    def update_bias_estimate(self, place_id: int, context_id: int, bias: np.ndarray):
        """Place + Context 조합의 bias 업데이트"""
        key = (place_id, context_id)
        if key not in self.context_memory:
            self.context_memory[key] = ContextMemory(place_id, context_id)
        self.context_memory[key].update_bias(bias)

@dataclass
class ContextMemory:
    place_id: int
    context_id: int
    bias_estimate: np.ndarray = field(default_factory=lambda: np.zeros(5))
    visit_count: int = 0
    last_visit_time: float = 0.0
```

#### 기대 효과

- Bias 학습이 서로 오염되지 않음
- 반복 가공 정밀도 문제 해결
- 현재 겪는 문제의 진짜 원인 해결

---

### ✅ 3단계: Replay / Consolidation

#### 목적

해마의 핵심 기능:
- "가만히 있을 때 더 똑똑해짐"
- 일시적 노이즈 필터링
- 진짜 편향만 장기 기억으로 고정

#### 구현 방향

1. **가공이 멈춘 휴지기에 학습된 bias 재검토**
   - `update()` 호출이 일정 시간 이상 없을 때 Replay 트리거
   - 예: `if time_since_last_update > replay_threshold: replay()`

2. **일시적 노이즈 필터링**
   - 여러 회차의 bias를 평균하여 노이즈 제거
   - 통계적 유의성 검증 (예: 표준 편차가 임계값 이하일 때만 저장)

3. **진짜 편향만 장기 기억으로 고정**
   - 일시적 노이즈는 제거하고, 지속적인 편향만 장기 기억에 저장
   - 장기 기억은 다음 날에도 유지

#### 구현 구조

```python
class ReplayConsolidation:
    def __init__(self):
        self.replay_threshold: float = 5.0  # 5초 이상 휴지기
        self.consolidation_window: int = 10  # 최근 10회차 평균
    
    def should_replay(self, last_update_time: float, current_time: float) -> bool:
        """Replay를 실행해야 하는지 판단"""
        return (current_time - last_update_time) > self.replay_threshold
    
    def replay(self, place_memory: Dict[int, PlaceMemory]):
        """휴지기에 기억 재검토 및 강화"""
        for place_id, memory in place_memory.items():
            if memory.visit_count >= self.consolidation_window:
                # 최근 N회차의 bias를 평균하여 노이즈 제거
                recent_biases = memory.get_recent_biases(self.consolidation_window)
                consolidated_bias = np.mean(recent_biases, axis=0)
                
                # 통계적 유의성 검증
                if self.is_significant(consolidated_bias, recent_biases):
                    memory.consolidated_bias = consolidated_bias
                    memory.consolidation_time = current_time
    
    def is_significant(self, bias: np.ndarray, recent_biases: List[np.ndarray]) -> bool:
        """편향이 통계적으로 유의한지 검증"""
        std = np.std(recent_biases, axis=0)
        return np.all(std < 0.001)  # 표준 편차가 임계값 이하
```

#### 기대 효과

- 장기 안정성 ↑
- 다음 날 더 잘 맞음
- Drift가 구조적으로 줄어듦

---

## 🏗️ 소뇌는 그 다음에

### 소뇌 구조

```
[ Place + Context + Bias Memory ]
            ↓
        Cerebellum
   (velocity / timing / prediction)
            ↓
          PID / Actuator
```

### 소뇌의 역할

이때 소뇌는:
- Grid를 흔들지 않고
- 기억을 깨지 않고
- "부드럽고 빠르게" 만든다

---

## 📋 구현 우선순위

1. **Place Cells** (가장 중요) ⭐⭐⭐
   - 반복 가공 정밀도 문제의 핵심 해결
   - 장소별 독립적인 bias 학습

2. **Context Binder** ⭐⭐
   - 기억 오염 방지
   - 반복 가공 정밀도 문제 완전 해결

3. **Replay/Consolidation** ⭐
   - 장기 안정성 향상
   - 다음 날 더 잘 맞음

---

## 🎯 핵심 명령

**"공간을 기억으로 승격시켜라"**

현재 상태에서 해야 할 일:
- 더 빠르게 ❌
- 더 고차원 ❌
- 더 정교한 기억 구조 ⭕

---

## 📝 참고

- 현재 구현: 해마 구조 구현의 상위 5% 이상
- 대부분의 사람은 Grid Cell도 못 만든다
- 지금 흔들리는 건 실패가 아니라 **"다음 계층으로 넘어가기 직전의 경계 상태"**다.

---

**Last Updated**: 2026-01-20  
**Status**: 계획 수립 완료, 구현 대기 중


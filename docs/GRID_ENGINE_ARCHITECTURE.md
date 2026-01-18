# Grid Engine 아키텍처: Reference Stabilizer 구조

**Grid Engine의 올바른 배치 및 침투 전략**

**Author**: GNJz  
**Created**: 2026-01-20  
**Version**: v0.4.0-alpha  
**Status**: Architecture Redesign

---

## 🎯 핵심 인사이트

**Grid Engine은 제어기(Controller)가 아닙니다.**

**Grid Engine의 정체**: 저주파 상태 기억 기반 Attractor Layer

---

## ❌ 실패한 구조 (현재 벤치마크)

### 구조도

```
Target (목표)
   ↓
PID Controller (오차 기반 제어)
   ↓
[ + Grid Engine Correction ]  ← ❌ 문제: 같은 축에서 충돌
   ↓
Actuator (모터)
```

### 문제점

1. **제어권 충돌**
   - PID: "지금 맞추려는 힘" (미래 지향)
   - Grid: "예전에 있던 상태로 돌아가려는 힘" (과거 지향)
   - → 서로 다른 목표를 동시에 밀어붙임

2. **오차 공간에서 작동**
   - Grid Engine이 `error`를 입력받음
   - Grid는 `position error minimizer`가 아님
   - Grid는 `state memory attractor`임

3. **결과**
   - RMS 오차 증가
   - 정착 오차 증가
   - 복귀 시간 동일

---

## ✅ 올바른 구조 (산업적으로 말이 되는 구조)

### 구조도

```
Target (목표)
   ↓
Trajectory Generator (궤적 생성)
   ↓
PID / MPC Controller (고주파 제어)
   ↓
Actuator (모터)
   ↑
Grid Engine (저주파, 상태 기준) ← ✅ Reference Stabilizer
   │
   └─→ Reference Correction (기준점 보정)
        ↓
        Target (미세 보정)
```

### 상세 흐름

```
1. Current State → Grid Engine
   │
   ├─ Grid Engine이 현재 상태를 위상 공간(T⁵)에 저장
   │
   └─ Grid Engine이 "마지막 안정 상태"를 기억

2. Grid Engine → Reference Correction
   │
   ├─ Grid Engine이 기억된 상태와 현재 상태 비교
   │
   └─ 차이를 Reference Correction으로 계산

3. Reference Correction → Target (미세 보정)
   │
   ├─ PID는 모르게, 참조 좌표만 이동
   │
   └─ PID는 보정된 타겟을 향해 최적 제어 수행
```

---

## 🔧 Grid Engine의 실제 역할

### 1. Reference Stabilizer (기준점 안정화)

**문제**:
- 열 변형
- 백래시
- 미세 드리프트

**해결**:
- Grid Engine이 "목표 좌표 자체"를 서서히 보정
- PID는 모르게, 참조 좌표만 이동
- 저주파 보정 (Grid Engine은 느린 주기)

### 2. Contact Recovery / Tool Re-entry

**문제**:
- 공구 접촉 후 튕김
- 충격 후 자세 붕괴

**해결**:
- Grid Engine이 "마지막 안정 가공 상태"를 기억
- 그 상태로 천천히 복귀
- PID는 고주파 제어, Grid는 저주파 복귀

### 3. 5축 동기 안정화 (Phase Coherence)

**문제**:
- PID는 축별 제어는 잘함
- 축 간 위상 일관성은 약함

**해결**:
- Grid Engine이 5축 전체를 하나의 위상 상태로 기억
- T⁵ 공간 전체의 위상 일관성 유지
- 이것은 PID로 절대 안 되는 영역

---

## 📊 데이터 흐름 (Reference Injection 방식)

### 단계별 흐름

```
Step 1: 상태 입력
   current_state → Grid Engine.update(current_state)

Step 2: 기준점 계산
   Grid Engine → provide_reference()
   │
   ├─ 기억된 안정 상태: φ_memory
   ├─ 현재 상태: φ_current
   └─ 차이: Δφ = φ_memory - φ_current

Step 3: Reference Correction
   Δφ → coordinate projection → reference_correction
   │
   └─ 미세 보정치 (저주파, 작은 가중치)

Step 4: Target 보정
   target_original + reference_correction → target_corrected

Step 5: PID 제어
   PID(target_corrected, current_state) → actuator_command
```

### 코드 구조 (의사 코드)

```python
# 올바른 구조
def control_loop():
    # 1. 현재 상태
    current_state = get_sensor_reading()
    
    # 2. Grid Engine 상태 업데이트 (저주파)
    if step % slow_cycle == 0:  # 저주파 (예: 10ms → 100ms)
        grid_engine.update(current_state)
        reference_correction = grid_engine.provide_reference()
    
    # 3. Target 보정 (Reference Injection)
    target_corrected = target_original + reference_correction * 0.1  # 작은 가중치
    
    # 4. PID 제어 (고주파)
    pid_output = pid_controller.control(target_corrected, current_state)
    
    # 5. Actuator 출력
    send_to_actuator(pid_output)
```

---

## 🎯 Grid Engine이 실제 CNC에서 쓰일 수 있는 지점

### ✅ 조건부 YES

**전제 조건**: Grid Engine이 Reference Stabilizer로 올바르게 배치되어야 함

### 활용 지점

#### ① Reference Stabilizer (기준점 안정화)

**문제**:
- 열 변형
- 백래시
- 미세 드리프트

**Grid Engine 역할**:
- "목표 좌표 자체"를 서서히 보정
- PID는 모르게, 참조 좌표만 이동
- 저주파 보정

#### ② Contact Recovery / Tool Re-entry

**문제**:
- 공구 접촉 후 튕김
- 충격 후 자세 붕괴

**Grid Engine 역할**:
- "마지막 안정 가공 상태"를 기억
- 그 상태로 천천히 복귀
- PID는 고주파 제어, Grid는 저주파 복귀

#### ③ 5축 동기 안정화 (Phase Coherence)

**문제**:
- PID는 축별 제어는 잘함
- 축 간 위상 일관성은 약함

**Grid Engine 역할**:
- 5축 전체를 하나의 위상 상태로 기억
- T⁵ 공간 전체의 위상 일관성 유지
- 이것은 PID로 절대 안 되는 영역

---

## 🔄 구조 비교

### ❌ 실패한 구조

```
Target → PID → (+ Grid correction) → Actuator
         ↑
         └─ Grid가 출력 경로에 직접 개입
```

**문제**: 제어권 충돌, 오차 증가

### ✅ 올바른 구조

```
Target → Trajectory Generator → PID → Actuator
         ↑                          ↑
         └─ Grid (Reference) ───────┘
            (저주파 보정)
```

**장점**: 
- PID는 고주파 제어 유지
- Grid는 저주파 기준점 보정
- 서로 간섭 없음

---

## 📋 구현 체크리스트

### 1단계: 구조 수정 (필수)

- [ ] Grid를 출력 경로에서 제거
- [ ] Grid → actuator 경로 차단
- [ ] Grid → reference / state memory로만 사용

### 2단계: 입력 변경

- [ ] Grid 입력을 error가 아니라 state로 변경
- [ ] `Grid.update(current_state)` 구현
- [ ] `Grid.provide_reference()` 구현

### 3단계: 벤치마크 재설계

- [ ] 비교 대상 변경:
  - PID Only
  - PID + Grid (Reference Drift Suppression)
- [ ] 측정 지표 변경:
  - 장기 RMS
  - thermal drift 대응
  - 반복 가공 정밀도

---

## 🎯 핵심 메시지

**Grid Engine은 제어기를 방해하지 않는 참조 안정화 기술입니다.**

현재 벤치마크의 실패는 이 사실을 증명하는 강력한 데이터입니다.

---

**Author**: GNJz  
**Made in GNJz**  
**Version**: v0.4.0-alpha  
**Last Updated**: 2026-01-20


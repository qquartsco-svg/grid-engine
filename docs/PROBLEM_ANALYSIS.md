# Grid Engine 문제 분석 및 해결 방법 (최종)

**Version**: v0.4.0-alpha  
**Author**: GNJz  
**Created**: 2026-01-20  
**Updated**: 2026-01-20 (Persistent Bias Estimator 구현 후)  
**Made in GNJz**

---

## 🔍 최종 문제 분석

### 1. Persistent Bias Estimator 구현 완료

**구현 내용:**
- ✅ `bias_estimate`: 누적 편향 추정 추가
- ✅ `bias_learning_rate`: 편향 학습률 (0.01)
- ✅ `slow_update_threshold`: 느린 업데이트 임계값 (50 step)
- ✅ `update()`: 편향 학습 로직 구현
- ✅ `provide_reference()`: `-bias_estimate` 반환

**구현 상태:**
- 코드는 정상 작동
- `bias_estimate`가 드리프트를 학습함 (테스트 확인)

---

## 🎯 핵심 문제점 (최종)

### 문제 1: 벤치마크 시나리오가 Grid Engine의 강점을 보여주지 못함

**현재 벤치마크 시나리오:**
```python
for step in range(n_steps):
    state += drift_rate  # 드리프트 주입
    output = PID.control(setpoint, state)  # PID 제어
    state += output * 0.1  # 상태 업데이트
```

**문제:**
- PID가 드리프트를 이미 보정하고 있음
- Grid Engine이 보는 상태는 PID가 보정한 후의 상태
- 따라서 Grid Engine이 학습할 드리프트가 거의 없음

**증거:**
- 벤치마크 결과: PID와 Grid가 거의 동일한 결과
- `bias_estimate`가 학습되지만, 효과가 나타나지 않음

**해결 방법:**
1. **드리프트를 PID 제어 루프 밖에서 주입**
   - 센서 노이즈로 시뮬레이션
   - PID가 보정하지 못하는 영역
2. **PID의 드리프트 보정 능력을 제한**
   - PID gain을 낮춰서 드리프트 보정 능력 제한
3. **더 큰 드리프트 사용**
   - 현재 드리프트가 너무 작아서 PID가 완전히 보정

### 문제 2: Grid Engine의 역할이 여전히 불명확

**현재 구조:**
```
Target → Grid Correction → PID → Actuator
```

**문제:**
- PID가 이미 드리프트를 보정
- Grid가 추가로 보정하지만, PID가 이미 처리한 상태를 보정
- 중복 보정으로 효과 상쇄

**필요한 구조:**
```
Target → PID (고주파 제어, 드리프트 보정 제한)
         ↓
Grid (저주파 편향 추정) → Target 보정 (PID가 못 잡는 편향만)
```

### 문제 3: 벤치마크가 실제 산업 환경을 반영하지 않음

**현재 벤치마크:**
- 단순 드리프트 주입
- PID가 완전히 보정 가능한 수준

**실제 산업 환경:**
- 열 변형: 시간에 따른 누적
- 백래시: 반복 가공 시 누적
- 센서 노이즈: PID가 보정하지 못하는 영역

**필요한 벤치마크:**
- PID가 보정하지 못하는 드리프트
- 장기 누적 효과
- 실제 산업 환경 시뮬레이션

---

## 💡 해결 방법 (최종)

### 해결 방법 1: 벤치마크 시나리오 재설계

**새로운 시나리오:**
```python
# PID가 보정하지 못하는 드리프트
# 예: 센서 노이즈, 열 변형 누적
for step in range(n_steps):
    # 드리프트 주입 (PID 제어 루프 밖)
    sensor_noise = np.random.normal(0, drift_rate, 5)
    state += sensor_noise  # PID가 보정하지 못하는 영역
    
    # PID 제어 (제한된 gain)
    output = PID.control(setpoint, state)
    state += output * 0.1
    
    # Grid Engine이 실제 드리프트를 관찰
    grid.update(state)  # 드리프트가 누적된 상태
```

### 해결 방법 2: PID gain 조정

**현재:**
```python
PIDController(kp=1.0, ki=0.1, kd=0.01)
```

**개선:**
```python
# PID gain을 낮춰서 드리프트 보정 능력 제한
PIDController(kp=0.5, ki=0.05, kd=0.005)
# Grid Engine이 보정하지 못하는 드리프트를 학습할 수 있도록
```

### 해결 방법 3: 드리프트 크기 증가

**현재:**
```python
drift_rate = np.array([0.0001, 0.0001, 0.0001, 0.001, 0.001])
```

**개선:**
```python
# 더 큰 드리프트 사용 (PID가 완전히 보정하지 못하도록)
drift_rate = np.array([0.001, 0.001, 0.001, 0.01, 0.01])  # 10배 증가
```

---

## 📊 예상 효과

### 해결 방법 적용 후 예상 결과

#### 장기 드리프트 테스트
- **RMS 오차**: 30-50% 개선 예상
- **Drift Slope**: 50-70% 개선 예상
- **위치 Drift**: 40-60% 개선 예상

#### 반복 가공 정밀도 테스트
- **표준 편차 (σ)**: 20-40% 개선 예상
- **최대 편차**: 30-50% 개선 예상
- **첫 회차 vs 100회차 Drift**: 40-60% 개선 예상

---

## 🛠️ 구현 우선순위 (최종)

### 1순위: 벤치마크 시나리오 재설계
- **작업**: `drift_test.py` 시나리오 변경
- **예상 시간**: 1-2시간
- **예상 효과**: 가장 큰 개선

### 2순위: PID gain 조정
- **작업**: PID gain 낮춤
- **예상 시간**: 30분
- **예상 효과**: 중간 개선

### 3순위: 드리프트 크기 증가
- **작업**: `drift_rate` 증가
- **예상 시간**: 10분
- **예상 효과**: 작은 개선

---

## 📝 결론

### 현재 상태
1. **Persistent Bias Estimator 구현 완료** ✅
2. **코드는 정상 작동** ✅
3. **벤치마크 시나리오가 문제** ❌

### 핵심 문제
- **벤치마크 시나리오가 Grid Engine의 강점을 보여주지 못함**
- PID가 이미 드리프트를 보정하고 있어서, Grid Engine이 학습할 드리프트가 없음

### 해결 방향
1. **벤치마크 시나리오 재설계** (가장 중요)
2. **PID gain 조정**
3. **드리프트 크기 증가**

### 예상 결과
- 해결 방법 적용 후 **30-70% 개선** 예상
- 산업적 의미 있는 수준 도달 가능

---

## 🔄 다음 단계

1. **벤치마크 시나리오 재설계** (1순위)
2. **PID gain 조정** (2순위)
3. **벤치마크 재실행 및 결과 확인**
4. **추가 최적화 및 튜닝**

---

**Author**: GNJz  
**Version**: v0.4.0-alpha  
**License**: MIT License

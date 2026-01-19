# 소뇌(Cerebellum) 설계 문서

**Date**: 2026-01-20  
**Version**: v0.5.0-alpha (Cerebellum Design)  
**Status**: 설계 단계

---

## 🎯 소뇌 설계 목표

**"해마의 기억을 즉각 행동으로 변환하는 계층"**

해마가 제공한 **"안정된 위상 지도"**와 **"정제된 장소 기억"**을 입력으로 받아, 실시간으로 다음을 수행:

1. **Predictive Feedforward**: 현재 속도와 가속도를 바탕으로 다음 순간의 오차를 예측
2. **Trial-to-Trial 보정**: 반복되는 궤적에서의 미세한 편차($\sigma$)를 극한으로 줄이는 순발력
3. **Variance 감소**: 해마가 영점을 잡는 동안 발생하는 미세한 떨림을 실시간 필터링

---

## 🧠 생물학적 배경

### 소뇌의 역할

**소뇌(Cerebellum)는**:
- ✅ 빠른 적응 (ms 단위)
- ✅ 순발력 (높은 주파수 제어 신호)
- ✅ Variance 감소 (미세한 떨림 제거)
- ✅ 예측 기반 피드포워드
- ❌ 장기 기억 형성 (해마 역할)
- ❌ 공간 표현 (Grid Engine 역할)

**핵심 관계**:
- 해마: "어디가 정상 상태였는가?" (느림, 분~시간~일)
- 소뇌: "지금 얼마나 벗어났는가?" (빠름, ms)
- 결합: "기억된 정상 상태를 지금 상황에 맞게 즉시 복원"

---

## 📐 소뇌 구조 설계

### 1. 입력 (Input)

**해마 메모리로부터**:
- `bias_estimate`: 기억된 편향 (Place/Context 기반)
- `consolidated_bias`: 정제된 장기 기억
- `place_id`: 현재 Place ID
- `context_id`: 현재 Context ID

**Grid Engine으로부터**:
- `current_state`: 현재 상태 [x, y, z, theta_a, theta_b]
- `target_state`: 목표 상태
- `phase_vector`: 현재 위상 벡터
- `velocity`: 현재 속도
- `acceleration`: 현재 가속도

**시스템으로부터**:
- `error`: 현재 오차 (target - current)
- `error_history`: 최근 오차 이력

---

### 2. 소뇌 핵심 기능

#### A. Predictive Feedforward

**역할**: 다음 순간의 오차를 예측하여 사전 보정

**수식**:
```
predicted_error = current_error + velocity * dt + 0.5 * acceleration * dt²
feedforward_correction = -predicted_error * feedforward_gain
```

**특징**:
- 해마의 기억된 bias를 바탕으로 예측 정확도 향상
- 속도/가속도 기반 예측
- ms 단위 빠른 반응

---

#### B. Trial-to-Trial 보정

**역할**: 반복되는 궤적에서의 미세한 편차를 극한으로 줄임

**수식**:
```
trial_error = current_error - memory_bias
trial_correction = -trial_error * trial_gain
```

**특징**:
- 해마의 기억된 bias와 현재 오차 비교
- 반복 작업에서 편차 누적 방지
- 순발력 제공

---

#### C. Variance 감소 (Jitter Filtering)

**역할**: 미세한 떨림을 실시간 필터링

**수식**:
```
filtered_error = low_pass_filter(current_error, cutoff_frequency)
variance_correction = -filtered_error * variance_gain
```

**특징**:
- 고주파 노이즈 제거
- 부드러운 제어 신호 생성
- 해마의 Place Blending과 시너지

---

#### D. 기억 기반 적응 (Memory-Based Adaptation)

**역할**: 해마의 기억을 즉각 행동으로 변환

**수식**:
```
memory_correction = -memory_bias * memory_gain
total_correction = feedforward_correction + trial_correction + variance_correction + memory_correction
```

**특징**:
- 해마의 기억을 실시간으로 활용
- 기억과 현재 상태의 차이를 즉각 보정
- 체감 가능한 성능 향상

---

### 3. 출력 (Output)

**제어 시스템으로**:
- `cerebellum_correction`: 소뇌 보정값
- `predicted_error`: 예측된 오차
- `variance_reduction`: 분산 감소량

**통합 제어**:
```
final_target = original_target + hippocampus_correction + cerebellum_correction
```

---

## 🔄 해마-소뇌 통합 구조

### 데이터 흐름

```
[Grid Engine] → [위상 벡터, 상태, 속도, 가속도]
                    ↓
[해마 메모리] → [기억된 bias, Place ID, Context ID]
                    ↓
[소뇌] → [예측, 보정, 필터링]
                    ↓
[제어 시스템] → [최종 제어 신호]
```

### 시간 스케일

| 계층 | 시간 스케일 | 역할 |
|------|-----------|------|
| **해마** | 느림 (분~시간~일) | 기준점 이동 |
| **소뇌** | 빠름 (ms) | 움직임 개선 |
| **Grid Engine** | 중간 (초) | 공간 표현 |

---

## 📊 소뇌 구현 계획

### Phase 1: 기본 소뇌 구조 (현재)

**구성 요소**:
1. `CerebellumEngine` 클래스
2. Predictive Feedforward
3. Trial-to-Trial 보정
4. Variance 감소

**인터페이스**:
```python
class CerebellumEngine:
    def __init__(self, memory: UniversalMemory):
        self.memory = memory
        # ...
    
    def compute_correction(
        self,
        current_state: np.ndarray,
        target_state: np.ndarray,
        velocity: np.ndarray,
        acceleration: np.ndarray,
        context: Dict[str, Any]
    ) -> np.ndarray:
        """소뇌 보정값 계산"""
        # 1. 해마에서 기억 검색
        memories = self.memory.retrieve(current_state, context)
        memory_bias = memories[0]['bias'] if memories else np.zeros(5)
        
        # 2. 예측 피드포워드
        predicted_error = self.predict_error(current_state, target_state, velocity, acceleration)
        
        # 3. Trial-to-Trial 보정
        trial_correction = self.compute_trial_correction(current_state, target_state, memory_bias)
        
        # 4. Variance 감소
        variance_correction = self.reduce_variance(current_state, target_state)
        
        # 5. 통합 보정
        total_correction = self.combine_corrections(
            predicted_error,
            trial_correction,
            variance_correction,
            memory_bias
        )
        
        return total_correction
```

---

### Phase 2: 고급 기능 (향후)

**구성 요소**:
1. 학습 메커니즘 (Online Learning)
2. 예측 모델 (Predictive Model)
3. 적응 제어 (Adaptive Control)

---

## 🎯 소뇌 설계 원칙

### 원칙 1: 해마를 존중

**소뇌는**:
- ✅ 해마의 기억을 활용
- ✅ 해마의 기억을 덮어쓰지 않음
- ✅ 해마의 기억을 보완

---

### 원칙 2: 빠른 적응

**소뇌는**:
- ✅ 실시간으로 빠르게 변화하는 상황에 즉각 대응
- ✅ ms 단위 반응
- ✅ 높은 주파수 제어 신호 생성

---

### 원칙 3: Variance 감소

**소뇌는**:
- ✅ 미세한 떨림 제거
- ✅ 부드러운 제어 신호 생성
- ✅ 해마의 Place Blending과 시너지

---

## 📋 구현 체크리스트

- [ ] CerebellumEngine 클래스 구현
- [ ] Predictive Feedforward 구현
- [ ] Trial-to-Trial 보정 구현
- [ ] Variance 감소 구현
- [ ] 해마 메모리 통합
- [ ] Grid Engine 통합
- [ ] 벤치마크 테스트
- [ ] 문서화

---

## 🚀 다음 단계

### 즉시 시작 가능

1. **CerebellumEngine 클래스 구현**
   - 기본 구조
   - 해마 메모리 통합
   - Predictive Feedforward

2. **Grid Engine 통합**
   - Grid5DEngine에 소뇌 추가
   - 해마-소뇌 통합 루프

3. **벤치마크 테스트**
   - 반응성 테스트
   - Variance 감소 테스트
   - 체감 성능 테스트

---

## 💡 핵심 인사이트

### 해마 vs 소뇌

**해마**:
- 느림 (분~시간~일)
- 기준점 이동
- 장기 안정성
- 체감 거의 없음

**소뇌**:
- 빠름 (ms)
- 움직임 개선
- 즉각 반응성
- 체감 즉각 있음

**결합**:
- "기억된 정상 상태를 지금 상황에 맞게 즉시 복원"
- 체감 가능한 성능 향상
- "와 이거 뭐야?" 제품 가능

---

## 📝 최종 목표

**"해마는 지도를 그렸고, 이제 소뇌가 그 지도 위에서 전력 질주할 차례입니다."**

**목표**:
- 해마의 기억을 즉각 행동으로 변환
- 체감 가능한 성능 향상
- "와 이거 뭐야?" 제품 완성

---

**Author**: GNJz  
**Made in**: GNJz  
**License**: MIT License


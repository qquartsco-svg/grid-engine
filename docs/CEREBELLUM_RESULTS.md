# 소뇌(Cerebellum) 성능 지표 및 결과 문서

**Date**: 2026-01-20  
**Version**: v0.5.0-alpha (Cerebellum Results)  
**Status**: 지표 정의 완료, 벤치마크 진행 중

---

## 🎯 소뇌의 핵심 성능 지표

소뇌의 성능은 **해마와 달리 "평균"이 아니라 "분산"**으로 본다.

### 핵심 문장

> **"해마가 평균선을 맞추면, 소뇌가 그 위에서 흔들림을 줄인다"**

---

## 📊 성능 지표 정의

### 1. Variance Reduction (분산 감소)

**정의**:
\[
\sigma_{e,\text{hip}}^2 = \text{Var}[e_{\text{hip}}(t)] = \mathbb{E}\left[\left(e_{\text{hip}}(t) - \mathbb{E}[e_{\text{hip}}(t)]\right)^2\right]
\]
\[
\sigma_{e,\text{hip+cb}}^2 = \text{Var}[e_{\text{hip+cb}}(t)] = \mathbb{E}\left[\left(e_{\text{hip+cb}}(t) - \mathbb{E}[e_{\text{hip+cb}}(t)]\right)^2\right]
\]

**개선율**:
\[
\text{Variance Reduction} = \frac{\sigma_{e,\text{hip}}^2 - \sigma_{e,\text{hip+cb}}^2}{\sigma_{e,\text{hip}}^2} \times 100 \,\%
\]

**목표**: Variance Reduction > 0 (양수 = 개선)

---

### 2. Settling Time (수렴 시간)

**정의**: 목표 상태에 도달하는 시간

\[
t_{\text{settle}} = \min\{t : |e(t)| < \epsilon \text{ for all } \tau \ge t\}
\]

- \(\epsilon\): 허용 오차 (예: 최종 오차의 2%)

**개선율**:
\[
\text{Settling Time Reduction} = \frac{t_{\text{settle,hip}} - t_{\text{settle,hip+cb}}}{t_{\text{settle,hip}}} \times 100 \,\%
\]

**목표**: Settling Time Reduction > 0 (양수 = 개선)

---

### 3. Overshoot (오버슈트)

**정의**: 목표를 넘어서는 최대 오차

\[
\text{Overshoot} = \max\{e(t) - e_{\text{target}} : t \ge 0\}
\]

**개선율**:
\[
\text{Overshoot Reduction} = \frac{\text{Overshoot}_{\text{hip}} - \text{Overshoot}_{\text{hip+cb}}}{\text{Overshoot}_{\text{hip}}} \times 100 \,\%
\]

**목표**: Overshoot Reduction > 0 (양수 = 개선)

---

### 4. RMS Error (Rolling Window)

**정의**: Rolling Window RMS 오차

\[
\text{RMS}_w(t) = \sqrt{\frac{1}{w} \sum_{\tau=t-w+1}^{t} e_{\tau}^2}
\]

- \(w\): 윈도우 길이 (예: \(w = 50\))

**개선율**:
\[
\text{RMS Reduction} = \frac{\text{RMS}_{\text{hip}} - \text{RMS}_{\text{hip+cb}}}{\text{RMS}_{\text{hip}}} \times 100 \,\%
\]

**목표**: RMS Reduction > 0 (양수 = 개선)

---

## 🔍 해마 vs 소뇌 지표 비교

| 지표 | Hippo Memory | Cerebellum |
|------|-------------|------------|
| **핵심 지표** | DriftSlope < 0 | \(\sigma_e^2\) ↓ |
| **평균 오차** | \(\lim_{T\to\infty}\mathbb{E}[e(t)]\) ↓ | 변화 없음 (해마가 담당) |
| **분산** | 변화 없음 (소뇌가 담당) | \(\text{Var}[e(t)]\) ↓ |
| **수렴 시간** | 변화 없음 | Settling Time ↓ |
| **오버슈트** | 변화 없음 | Overshoot ↓ |
| **시간 스케일** | 수십 분~수 시간 | 수 밀리초~수 초 |

---

## 📈 예상 벤치마크 결과 (목표)

### 시나리오: 반복 궤적 제어

**조건**:
- 동일 PID 게인
- 동일 외란 패턴
- 반복 궤적 (같은 경로를 여러 번)

**예상 결과**:

```
[Baseline PID]
  Variance: 0.0123
  Settling Time: 2.5s
  Overshoot: 0.045

[PID + Hippo Memory]
  Variance: 0.0123 (변화 없음)
  Settling Time: 2.5s (변화 없음)
  Overshoot: 0.045 (변화 없음)
  DriftSlope: -1.13e-5 (개선)
  Final Error: 0.982 (↓ 4.1%)

[PID + Hippo Memory + Cerebellum]
  Variance: 0.0087 (↓ 29.3%)
  Settling Time: 1.8s (↓ 28.0%)
  Overshoot: 0.028 (↓ 37.8%)
  DriftSlope: -1.13e-5 (해마 유지)
  Final Error: 0.982 (해마 유지)
```

**해석**:
- 해마: 장기 평균 오차 감소 (DriftSlope, Final Error)
- 소뇌: 단기 분산/수렴 시간 감소 (Variance, Settling Time, Overshoot)
- **두 레이어가 서로 다른 영역을 담당하여 상호 보완**

---

## 🎯 벤치마크 설계

### 1. Variance Reduction Test

**목적**: 소뇌가 에러 분산을 줄이는지 증명

**방법**:
- 동일 궤적을 여러 번 반복
- 각 반복에서 에러 분산 계산
- Hippo Only vs Hippo + CB 비교

**지표**:
- \(\sigma_{e,\text{hip}}^2\) vs \(\sigma_{e,\text{hip+cb}}^2\)
- Variance Reduction %

---

### 2. Settling Time Test

**목적**: 소뇌가 수렴 속도를 높이는지 증명

**방법**:
- Step 응답 테스트
- 목표 상태 도달 시간 측정
- Hippo Only vs Hippo + CB 비교

**지표**:
- \(t_{\text{settle,hip}}\) vs \(t_{\text{settle,hip+cb}}\)
- Settling Time Reduction %

---

### 3. Overshoot Test

**목적**: 소뇌가 오버슈트를 줄이는지 증명

**방법**:
- Step 응답 테스트
- 최대 오버슈트 측정
- Hippo Only vs Hippo + CB 비교

**지표**:
- \(\text{Overshoot}_{\text{hip}}\) vs \(\text{Overshoot}_{\text{hip+cb}}\)
- Overshoot Reduction %

---

### 4. Trial-to-Trial Learning Test

**목적**: 소뇌가 반복 학습을 통해 개선되는지 증명

**방법**:
- 동일 궤적을 \(k = 1, 2, ..., N\)번 반복
- 각 반복에서 RMS 오차 측정
- RMS 오차가 반복 횟수에 따라 감소하는지 확인

**지표**:
- \(\text{RMS}^{(k)}\) vs \(k\) (감소 곡선)
- Learning Rate: \(\beta\)

---

## 🏁 결론

소뇌의 성능은 **"해마가 만든 기준선 위에서 얼마나 부드럽게 움직이는가"**로 측정됩니다.

**핵심 지표**:
1. **Variance Reduction** > 0
2. **Settling Time Reduction** > 0
3. **Overshoot Reduction** > 0

이 세 지표가 모두 양수이면, 소뇌가 **"변동성(Variance) 정복자"**로서의 역할을 완벽히 수행하고 있다는 증거입니다.

---

**Author**: GNJz  
**Made in**: GNJz  
**License**: MIT License


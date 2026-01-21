# 소뇌(Cerebellum) 설계 및 포지션 문서

**Date**: 2026-01-20  
**Version**: v0.5.0-alpha (Cerebellum Design)  
**Status**: 설계 완료, 구현 진행 중

---

## 🎯 소뇌의 정확한 포지션

### 핵심 문장

> **"해마가 기준선을 만들고, 소뇌가 그 위에서 움직임을 다듬는다"**

### 3-레이어 제어 구조의 시간·주파수 분해

| 레이어 | 담당 시간대 | 핵심 목표 | 제거 대상 |
|--------|------------|----------|----------|
| **PID** | 고주파 / 즉각 | 즉시 안정화 | 순간 오차, 발산 |
| **Cerebellum** | 단·중기 | 빠른 수렴, 흔들림 감소 | 진동, 오버슈트, 분산 |
| **Hippo Memory** | 저주파 / 장기 | 평균선 보정 | bias, drift |

**시간 스케일 관계**:
\[
\tau_{\text{PID}} \ll \tau_{\text{cb}} \ll \tau_{\text{hip}}
\]

- PID: 밀리초(ms) 단위 즉각 반응
- Cerebellum: 수 밀리초~수 초 단위 빠른 적응
- Hippo Memory: 수십 분~수 시간 단위 장기 기억

---

## 📐 수식적 확정: 제어 신호의 가산(Additive) 구조

### 최종 제어 공식

소뇌는 기존 제어 루프를 파괴하지 않고, **병렬로 붙는 가속기** 역할을 합니다.

\[
u(t) = u_{\text{PID}}(t) + u_{\text{cb}}(t)
\]

- \(u_{\text{PID}}(t)\): PID 제어기 출력 (기존 제어기, 건드리지 않음)
- \(u_{\text{cb}}(t)\): 소뇌 보정 신호 (추가 가속기)

### 소뇌 출력 수식

\[
u_{\text{cb}}(t) = f_{\theta}\left( x(t), \dot{x}(t), \ddot{x}(t), \{e_{\text{hip}}(t-k)\}, b_{\text{hip}}(x(t),c(t)) \right)
\]

**입력**:
- \(x(t), \dot{x}(t), \ddot{x}(t)\): 현재 상태, 속도, 가속도
- \(\{e_{\text{hip}}(t-k)\}\): 최근 에러 히스토리
- \(b_{\text{hip}}(x(t),c(t))\): 해마가 제공한 장소/맥락별 편향 (선택적)

**출력**:
- \(u_{\text{cb}}(t)\): 추가 제어 신호

**포지션**: PID가 놓치는 **'비선형적 잔차'**와 **'반복적 오차 패턴'**을 실시간으로 상쇄하는 **Active Damper(능동형 댐퍼)** 역할.

---

## 🧠 소뇌가 책임지는 3가지 핵심 기능

### 1. Predictive Feedforward (예측 보정)

**역할**: 아직 발생하지 않은 오차를 미리 예측하여 사전 보정

**수식**:
\[
e_{\text{pred}}(t+\Delta t) = e_{\text{hip}}(t) + \dot{x}(t) \cdot \Delta t + \frac{1}{2} \ddot{x}(t) \cdot (\Delta t)^2
\]
\[
u_{\text{cb}}^{\text{ff}}(t) = -f_{\theta}\left( e_{\text{pred}}(t+\Delta t), b_{\text{hip}}(x(t),c(t)) \right) \cdot \alpha_{\text{ff}}
\]

- \(e_{\text{pred}}(t+\Delta t)\): 예측된 오차
- \(\Delta t\): 예측 시간 (예: 0.01초)
- \(\alpha_{\text{ff}}\): Feedforward gain
- \(f_{\theta}\): 소뇌 예측 함수 (선형 근사, 작은 NN, 테이블 등 교체 가능)

**핵심 문장**:
> **"PID는 틀린 다음에 고치고, 소뇌는 틀릴 걸 알고 먼저 고친다"**

---

### 2. Trial-to-Trial Learning (회차 학습)

**역할**: 반복되는 궤적에서의 미세한 편차를 극한으로 줄임

**수식**:
\[
\bar{e}^{(k)} = \frac{1}{T} \sum_{t=1}^{T} e_{\text{hip}}^{(k)}(t)
\]
\[
\Delta u_{\text{cb}}^{(k+1)} = \beta \cdot \bar{e}^{(k)}
\]
\[
u_{\text{cb}}^{(k+1)}(t) = u_{\text{cb}}^{(k)}(t) + \Delta u_{\text{cb}}^{(k+1)}
\]

- \(\bar{e}^{(k)}\): \(k\)번째 반복(회차)의 평균 오차
- \(\beta\): Trial 학습률
- \(u_{\text{cb}}^{(k)}(t)\): \(k\)번째 반복에서의 소뇌 보정

**효과**:
- 같은 작업을 할수록 더 잘함
- CNC, 로봇, 반복 제어에 최적
- 해마가 "어디서 문제였는지" 알려주면, 소뇌는 "다음엔 어떻게 움직일지" 학습

---

### 3. Variance Reduction (분산 감소 - 핵심 지표)

**역할**: 해마가 기준선을 맞춘 이후 구간에서, 에러의 **분산(흔들림)**을 줄임

**수식**:
\[
\sigma_{e,\text{hip}}^2 = \text{Var}[e_{\text{hip}}(t)] \quad\text{(Hippo Only)}
\]
\[
\sigma_{e,\text{hip+cb}}^2 = \text{Var}[e_{\text{hip+cb}}(t)] \quad\text{(Hippo + Cerebellum)}
\]

**목표**:
\[
\sigma_{e,\text{hip+cb}}^2 < \sigma_{e,\text{hip}}^2
\]

→ **"같은 기준선에서 더 덜 흔들린다"**를 수치로 증명

**구현**:
- 저주파 필터 (Low-pass filter)
- 이동 평균 필터
- 고주파 노이즈 제거

\[
e_{\text{filtered}}(t) = \text{LPF}(e_{\text{hip}}(t))
\]
\[
u_{\text{cb}}^{\text{var}}(t) = -\left( e_{\text{hip}}(t) - e_{\text{filtered}}(t) \right) \cdot \alpha_{\text{var}}
\]

- \(\alpha_{\text{var}}\): Variance 감소 gain

---

## ⚠️ Hippo vs Cerebellum — 절대 헷갈리면 안 되는 경계

| 구분 | Hippo Memory | Cerebellum |
|------|-------------|------------|
| **다루는 것** | 평균 (Bias) | 분산 (Variance) |
| **시간 스케일** | 아주 느림 (\(\tau_{\text{hip}} \gg \tau_{\text{PID}}\)) | 빠름 (\(\tau_{\text{cb}} \sim \tau_{\text{PID}}\)) |
| **기억 대상** | 장소/맥락 | 동작 패턴 |
| **목표** | DriftSlope < 0 | RMS/Var ↓, Settling Time ↓ |
| **개입 위치** | 측정값 (오차 정의) | 제어 입력 (제어 신호) |
| **핵심 지표** | \(\lim_{T\to\infty}\mathbb{E}[e(t)]\) | \(\text{Var}[e(t)]\), Settling Time |

### 결정적 문장

- ❌ **소뇌는 bias를 고치지 않는다** (해마 역할)
- ❌ **해마는 진동을 줄이지 않는다** (소뇌 역할)

- ⭕ **해마가 기준선을 만들고**
- ⭕ **소뇌가 그 위에서 움직임을 다듬는다**

---

## 🎯 성능 지표의 전환: "Bias에서 Variance로"

### 해마의 성능 지표

- **DriftSlope** < 0: 장기 평균 오차의 하강
- **Final Error** ↓: 최종 편향 감소
- **물리적 효과**: 영점 보정, 열변형 극복

### 소뇌의 성능 지표

- **Settling Time** ↓: 목표에 도달하는 시간 단축
- **\(\sigma_e^2\)** ↓: 에러 분산 감소
- **Overshoot** ↓: 오버슈트 감소
- **물리적 효과**: 진동 억제, 오버슈트 방지, 쾌속 응답

---

## 📦 모듈/제품 포지션 문장 (확정본)

### Hippo Memory
→ **Long-Horizon Bias Compensation Engine**

### Cerebellum Module
→ **Fast Convergence & Vibration Smoothing Accelerator**

**공통점**:
- PID 교체 ❌
- 기존 제어기 옆에 꽂는 모듈 ⭕
- 독립 상품화 가능 ⭕
- 교체·업그레이드 가능 ⭕

---

## 🔧 구현 구조

### 입력 (Input)

- **상태/측정**: \(x(t), y(t)\)
- **히스토리 에러**: \(\{e_{\text{hip}}(t-k)\}_{k=0}^{K-1}\)
- **동역학 힌트**: \(\dot{x}(t), \ddot{x}(t)\)
- **(선택) 해마 출력**: \(b_{\text{hip}}(x,c)\)

### 출력 (Output)

- **추가 제어 신호**: \(u_{\text{cb}}(t)\)

### 내부 구조

- **\(f_{\theta}\)**: Feedforward 예측기 (교체 가능)
- **Trial Memory**: 최근 궤적/에러 집계
- **Low-pass Filter**: Variance 감소 필터

---

## 🏁 결론

소뇌는 **"지능형 제어의 완성"**을 위한 마지막 퍼즐 조각입니다.

- **해마**: "기준선(Bias) 수호자"
- **소뇌**: "변동성(Variance) 정복자"

이 두 레이어가 결합되면:
- 장기적으로 안정된 기준선 (해마)
- 그 위에서 빠르고 부드러운 움직임 (소뇌)

→ **완전체 지능형 제어기** 완성

---

**Author**: GNJz  
**Made in**: GNJz  
**License**: MIT License

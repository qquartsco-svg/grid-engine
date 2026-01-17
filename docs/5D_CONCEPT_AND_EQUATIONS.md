# 5D Grid Engine 개념 및 수식

**5D Grid Engine = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B**

5축 CNC 제어를 위한 5차원 공간 상태 메모리 엔진

**Author: GNJz**  
**Created: 2026-01-20**  
**Made in GNJz**  
**Version: v0.4.0-alpha (5D extension)**  
**License: MIT License**

---

## 1. 구조적 관계

### 1.1 차원별 확장

```
2D: Grid = Ring X ⊗ Ring Y
3D: Grid 3D = Ring X ⊗ Ring Y ⊗ Ring Z
4D: Grid 4D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring W
5D: Grid 5D = Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B ✨ NEW
```

### 1.2 5축 CNC 매핑

**5축 CNC 구조**:
- **위치 축 (3개)**: X, Y, Z (선형 이동)
- **회전 축 (2개)**: A, B (각도 회전)

**Ring 매핑**:
- Ring X: X축 위치 위상 안정화
- Ring Y: Y축 위치 위상 안정화
- Ring Z: Z축 위치 위상 안정화
- Ring A: A축 회전 위상 안정화 (X축 기준 회전, Tilt)
- Ring B: B축 회전 위상 안정화 (Y축 기준 회전, Rotary)

---

## 2. 위상 공간

### 2.1 5차원 위상 공간

**위상 벡터**:
\[
\vec{\phi}(t) = (\phi_x(t), \phi_y(t), \phi_z(t), \phi_a(t), \phi_b(t)) \in T^5
\]

여기서 \(T^5 = S^1 \times S^1 \times S^1 \times S^1 \times S^1\)는 5차원 토러스입니다.

**위상 범위**:
\[
\phi_x, \phi_y, \phi_z, \phi_a, \phi_b \in [0, 2\pi)
\]

### 2.2 물리적 의미

- **위치 위상** (\(\phi_x, \phi_y, \phi_z\)): 선형 위치를 위상으로 표현
- **회전 위상** (\(\phi_a, \phi_b\)): 회전 각도를 위상으로 표현

---

## 3. 좌표 변환

### 3.1 위치 좌표 변환

**위상 → 위치**:
\[
x = \phi_x \cdot \frac{L_x}{2\pi}
\]
\[
y = \phi_y \cdot \frac{L_y}{2\pi}
\]
\[
z = \phi_z \cdot \frac{L_z}{2\pi}
\]

여기서 \(L_x, L_y, L_z\)는 각 축의 공간 스케일 [m]입니다.

**위치 → 위상**:
\[
\phi_x = x \cdot \frac{2\pi}{L_x}
\]
\[
\phi_y = y \cdot \frac{2\pi}{L_y}
\]
\[
\phi_z = z \cdot \frac{2\pi}{L_z}
\]

### 3.2 회전 각도 변환

**위상 → 각도**:
\[
\theta_a = \phi_a \cdot \frac{360°}{2\pi} = \phi_a \cdot \frac{180°}{\pi}
\]
\[
\theta_b = \phi_b \cdot \frac{360°}{2\pi} = \phi_b \cdot \frac{180°}{\pi}
\]

**각도 → 위상**:
\[
\phi_a = \theta_a \cdot \frac{2\pi}{360°} = \theta_a \cdot \frac{\pi}{180°}
\]
\[
\phi_b = \theta_b \cdot \frac{2\pi}{360°} = \theta_b \cdot \frac{\pi}{180°}
\]

**주의**: 회전 축은 주기적이므로 각도는 \([-180°, 180°)\) 또는 \([0°, 360°)\) 범위로 정규화됩니다.

---

## 4. 경로 통합 (Path Integration)

### 4.1 뉴턴 제2법칙 (5D 확장)

**위치 축 (X, Y, Z)**:
\[
v_x(t+\Delta t) = v_x(t) + a_x(t) \cdot \Delta t
\]
\[
v_y(t+\Delta t) = v_y(t) + a_y(t) \cdot \Delta t
\]
\[
v_z(t+\Delta t) = v_z(t) + a_z(t) \cdot \Delta t
\]

\[
\phi_x(t+\Delta t) = \phi_x(t) + v_x(t) \cdot \Delta t + \frac{1}{2}a_x(t) \cdot (\Delta t)^2
\]
\[
\phi_y(t+\Delta t) = \phi_y(t) + v_y(t) \cdot \Delta t + \frac{1}{2}a_y(t) \cdot (\Delta t)^2
\]
\[
\phi_z(t+\Delta t) = \phi_z(t) + v_z(t) \cdot \Delta t + \frac{1}{2}a_z(t) \cdot (\Delta t)^2
\]

**회전 축 (A, B)**:
\[
v_a(t+\Delta t) = v_a(t) + \alpha_a(t) \cdot \Delta t
\]
\[
v_b(t+\Delta t) = v_b(t) + \alpha_b(t) \cdot \Delta t
\]

\[
\phi_a(t+\Delta t) = \phi_a(t) + v_a(t) \cdot \Delta t + \frac{1}{2}\alpha_a(t) \cdot (\Delta t)^2
\]
\[
\phi_b(t+\Delta t) = \phi_b(t) + v_b(t) \cdot \Delta t + \frac{1}{2}\alpha_b(t) \cdot (\Delta t)^2
\]

여기서:
- \(v_x, v_y, v_z\): 위치 속도 [m/s]
- \(a_x, a_y, a_z\): 위치 가속도 [m/s²]
- \(v_a, v_b\): 각속도 [rad/s] 또는 [deg/s]
- \(\alpha_a, \alpha_b\): 각가속도 [rad/s²] 또는 [deg/s²]

### 4.2 Semi-implicit Euler 적분 (5D)

**속도 업데이트**:
\[
v_x^{n+1} = v_x^n + a_x^n \cdot \Delta t
\]
\[
v_y^{n+1} = v_y^n + a_y^n \cdot \Delta t
\]
\[
v_z^{n+1} = v_z^n + a_z^n \cdot \Delta t
\]
\[
v_a^{n+1} = v_a^n + \alpha_a^n \cdot \Delta t
\]
\[
v_b^{n+1} = v_b^n + \alpha_b^n \cdot \Delta t
\]

**위상 업데이트**:
\[
\phi_x^{n+1} = \phi_x^n + v_x^n \cdot \Delta t + \frac{1}{2}a_x^n \cdot (\Delta t)^2
\]
\[
\phi_y^{n+1} = \phi_y^n + v_y^n \cdot \Delta t + \frac{1}{2}a_y^n \cdot (\Delta t)^2
\]
\[
\phi_z^{n+1} = \phi_z^n + v_z^n \cdot \Delta t + \frac{1}{2}a_z^n \cdot (\Delta t)^2
\]
\[
\phi_a^{n+1} = \phi_a^n + v_a^n \cdot \Delta t + \frac{1}{2}\alpha_a^n \cdot (\Delta t)^2
\]
\[
\phi_b^{n+1} = \phi_b^n + v_b^n \cdot \Delta t + \frac{1}{2}\alpha_b^n \cdot (\Delta t)^2
\]

---

## 5. Ring 안정화

### 5.1 5개 Ring Attractor

각 축마다 독립적인 Ring Attractor가 위상을 안정화합니다:

\[
\text{Ring X}: \phi_x \rightarrow \phi_x^{\text{stable}}
\]
\[
\text{Ring Y}: \phi_y \rightarrow \phi_y^{\text{stable}}
\]
\[
\text{Ring Z}: \phi_z \rightarrow \phi_z^{\text{stable}}
\]
\[
\text{Ring A}: \phi_a \rightarrow \phi_a^{\text{stable}}
\]
\[
\text{Ring B}: \phi_b \rightarrow \phi_b^{\text{stable}}
\]

### 5.2 위상 정규화

모든 위상은 \([0, 2\pi)\) 범위로 정규화됩니다:

\[
\phi_x = \phi_x \bmod 2\pi
\]
\[
\phi_y = \phi_y \bmod 2\pi
\]
\[
\phi_z = \phi_z \bmod 2\pi
\]
\[
\phi_a = \phi_a \bmod 2\pi
\]
\[
\phi_b = \phi_b \bmod 2\pi
\]

---

## 6. 에너지 함수

### 6.1 5D 에너지 함수

각 Ring의 에너지를 합산:

\[
E_{\text{total}} = E_x + E_y + E_z + E_a + E_b
\]

여기서 각 \(E_i\)는 해당 Ring의 에너지 함수입니다.

### 6.2 열역학적 안정성

에너지 감소 조건:
\[
\frac{dE_{\text{total}}}{dt} \leq 0
\]

이것은 열역학 제2법칙 (국소 엔트로피 감소)과 일치합니다.

---

## 7. 5축 CNC 응용

### 7.1 진동 억제

Ring Attractor가 위상을 안정화하여 진동을 억제합니다:
- 진동 → 위상 변화 → Ring이 안정화 → 진동 억제

### 7.2 노이즈 억제

센서 노이즈가 위상에 영향을 주어도 Ring이 노이즈를 흡수합니다:
- 노이즈 → 위상 변화 → Ring이 흡수 → 노이즈 억제

### 7.3 외란 억제

절삭력 변동, 백래시, 열 변형 등 외란에 강건합니다:
- 외란 → 위상 변화 → Ring이 안정화 → 외란 억제

---

## 8. 수식 요약

### 8.1 핵심 수식

**위상 공간**: \(T^5 = S^1 \times S^1 \times S^1 \times S^1 \times S^1\)

**위상 벡터**: \(\vec{\phi} = (\phi_x, \phi_y, \phi_z, \phi_a, \phi_b)\)

**위치 변환**: \(x = \phi_x \cdot (L_x / 2\pi)\), \(y = \phi_y \cdot (L_y / 2\pi)\), \(z = \phi_z \cdot (L_z / 2\pi)\)

**각도 변환**: \(\theta_a = \phi_a \cdot (180° / \pi)\), \(\theta_b = \phi_b \cdot (180° / \pi)\)

**경로 통합**: \(\phi^{n+1} = \phi^n + v^n \cdot \Delta t + \frac{1}{2}a^n \cdot (\Delta t)^2\) (5축)

**에너지**: \(E_{\text{total}} = \sum_{i \in \{x,y,z,a,b\}} E_i\)

---

## 9. 뉴턴 제2법칙과의 연관성

Grid 5D Engine은 뉴턴 제2법칙 (F = ma)을 5차원 위상 공간에 구현한 물리 기반 제어 엔진입니다.

**물리적 대응 관계**:
- 위치 r → 위상 φ (phase) [rad]
- 속도 v → 속도 입력 (velocity) [m/s] 또는 [deg/s]
- 가속도 a → 가속도 입력 (accel) [m/s²] 또는 [deg/s²]
- 힘 F → 외란 (disturbance) [N] 또는 [N·m]

**상태 방정식**:
\[
\frac{d\vec{\phi}}{dt} = \vec{v}(t)
\]
\[
\frac{d\vec{v}}{dt} = \vec{a}(t)
\]

여기서 \(\vec{\phi} = (\phi_x, \phi_y, \phi_z, \phi_a, \phi_b)\), \(\vec{v} = (v_x, v_y, v_z, v_a, v_b)\), \(\vec{a} = (a_x, a_y, a_z, \alpha_a, \alpha_b)\)입니다.

---

## 10. 요약

**5D Grid Engine**:
- 구조: Ring X ⊗ Ring Y ⊗ Ring Z ⊗ Ring A ⊗ Ring B
- 위상 공간: T⁵ (5차원 토러스)
- 응용: 5축 CNC 제어 (진동/노이즈/외란 억제)
- 물리 기반: 뉴턴 제2법칙 (위치 + 회전)

**핵심 메시지**:
"5축 CNC는 정확히 Ring 5개로 표현 가능합니다.
이것은 단순한 확장이 아니라,
산업 제어의 혁신적 접근입니다."

---

**Author: GNJz**  
**Created: 2026-01-20**  
**Made in GNJz**  
**Version: v0.4.0-alpha (5D extension)**  
**License: MIT License**


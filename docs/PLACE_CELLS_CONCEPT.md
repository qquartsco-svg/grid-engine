# Place Cells 개념 및 수식 (Place Cells Concept and Equations)

**Version**: v0.4.0-alpha  
**Author**: GNJz  
**Created**: 2026-01-20  
**Made in GNJz**

---

## 🎯 개요

**Place Cells (장소 세포)**는 해마의 CA1 영역에 있는 뉴런으로, 동물이 특정 공간 위치에 있을 때 활성화됩니다. Grid Engine에서 Place Cells는 Grid Cells의 위상 공간을 장소별로 분류하여, 장소별 독립적인 기억(bias)을 저장하는 역할을 합니다.

**핵심 목적**:
- Grid는 '좌표계' (연속적인 위상 공간)
- Place는 '장소 ID' (특정 위치를 고유하게 식별)
- 반복 가공 시 동일 지점의 편향을 불러오기
- 회차 간 학습이 가능하도록

---

## 📊 생물학적 배경

### Place Cells의 특징

1. **특정 위치에서 발화**: 동물이 특정 공간 위치에 있을 때만 활성화
2. **Place Field (장소 필드)**: Place Cell이 활성화되는 공간 영역
3. **Grid Cell과의 관계**: Grid Cell의 활성화 패턴이 Place Cell의 발화를 결정
4. **기억과의 연결**: Place Cell의 활성화는 해당 장소의 기억을 불러옴

### Grid Cells vs Place Cells

| 특징 | Grid Cells | Place Cells |
|------|-----------|-------------|
| **역할** | 공간 표현의 기본 단위 | 특정 위치 표현 |
| **활성화** | 정육각형 격자 패턴 | 특정 위치에서만 발화 |
| **범위** | 전체 공간을 커버 | 특정 장소 영역 (Place Field) |
| **기억** | 위치 정보만 | 위치 + 기억 (bias) |

---

## 🔬 수학적 모델

### 1. Place Field 정의

Place Cell $i$의 Place Field는 위상 공간에서 특정 영역 $\mathcal{R}_i$로 정의됩니다:

\[
\mathcal{R}_i = \{\Phi \in \mathbb{T}^n : \| \Phi - \Phi_i \| < r_i \}
\]

여기서:
- $\Phi = (\phi_x, \phi_y, \phi_z, \phi_a, \phi_b)$: 현재 위상 벡터 (5D)
- $\Phi_i$: Place Cell $i$의 중심 위상 벡터
- $r_i$: Place Field의 반경 (rad)
- $\mathbb{T}^n$: n차원 토러스 ($n=5$ for 5D)

### 2. Place ID 할당

Place ID는 위상 공간을 해시하거나 클러스터링하여 생성합니다:

**방법 1: 위상 공간 해싱**

\[
\text{place\_id} = \text{hash}(\Phi) \bmod N
\]

여기서:
- $N$: 최대 Place Cell 수 (예: 1000)
- `hash()`: 위상 벡터를 정수로 변환하는 해시 함수

**구현 예시**:
```python
def get_place_id(phase_vector: np.ndarray, num_places: int = 1000) -> int:
    """위상 벡터를 Place ID로 변환"""
    # 위상 벡터를 정수 배열로 변환 (소수점 이하 자릿수 처리)
    phase_int = (phase_vector * 1000).astype(int)
    # 해시 함수 적용
    place_hash = hash(tuple(phase_int))
    # 모듈로 연산으로 Place ID 생성
    place_id = place_hash % num_places
    return place_id
```

**방법 2: 클러스터링 기반 할당**

위상 공간을 영역으로 분할하고, 가장 가까운 클러스터 중심을 Place ID로 사용:

\[
\text{place\_id} = \arg\min_i \| \Phi - \Phi_i \|
\]

**구현 예시** (K-means 클러스터링):
```python
def get_place_id_clustering(
    phase_vector: np.ndarray,
    cluster_centers: np.ndarray  # Shape: (N, 5)
) -> int:
    """클러스터링 기반 Place ID 할당"""
    distances = np.linalg.norm(cluster_centers - phase_vector, axis=1)
    place_id = np.argmin(distances)
    return place_id
```

### 3. Place Cell 활성화 함수

Place Cell $i$의 활성화 강도는 현재 위상 벡터와 Place Field 중심의 거리에 따라 결정됩니다:

\[
a_i(\Phi) = \exp\left(-\frac{\|\Phi - \Phi_i\|^2}{2\sigma_i^2}\right)
\]

여기서:
- $a_i(\Phi)$: Place Cell $i$의 활성화 강도 [0, 1]
- $\sigma_i$: Place Field의 폭 (rad)
- $\|\Phi - \Phi_i\|$: 현재 위상 벡터와 Place Field 중심의 거리

**구현 예시**:
```python
def place_cell_activation(
    phase_vector: np.ndarray,
    place_center: np.ndarray,
    sigma: float = 0.1  # Place Field 폭 (rad)
) -> float:
    """Place Cell 활성화 강도 계산"""
    distance = np.linalg.norm(phase_vector - place_center)
    activation = np.exp(-(distance ** 2) / (2 * sigma ** 2))
    return activation
```

### 4. Place별 Bias 저장 및 불러오기

각 Place ID마다 독립적인 bias 추정값을 저장:

\[
b_{\text{place}}(\text{place\_id}) = \begin{cases}
b_{\text{new}} & \text{if first visit} \\
\alpha \cdot b_{\text{new}} + (1-\alpha) \cdot b_{\text{old}} & \text{otherwise}
\end{cases}
\]

여기서:
- $b_{\text{place}}(\text{place\_id})$: Place ID별 bias 추정값
- $b_{\text{new}}$: 현재 학습된 bias
- $b_{\text{old}}$: 기존 저장된 bias
- $\alpha$: 학습률 (예: 0.1)

**구현 예시**:
```python
@dataclass
class PlaceMemory:
    place_id: int
    bias_estimate: np.ndarray = field(default_factory=lambda: np.zeros(5))
    visit_count: int = 0
    last_visit_time: float = 0.0
    stable_state_snapshot: Optional[Grid5DState] = None
    
    def update_bias(self, new_bias: np.ndarray, learning_rate: float = 0.1):
        """Place별 bias 업데이트"""
        if self.visit_count == 0:
            # 첫 방문: 새로운 bias 그대로 저장
            self.bias_estimate = new_bias.copy()
        else:
            # 이후 방문: 지수 이동 평균으로 업데이트
            self.bias_estimate = (
                learning_rate * new_bias + 
                (1 - learning_rate) * self.bias_estimate
            )
        self.visit_count += 1
```

---

## 🏗️ Grid Engine 통합 구조

### 현재 구조 (Place Cells 없음)

```python
class Grid5DEngine:
    def __init__(self):
        # 전역 단일 bias 추정값
        self.bias_estimate: np.ndarray = np.zeros(5)  # ❌ 문제점
    
    def update(self, current_state: np.ndarray):
        # 모든 장소의 bias가 하나의 벡터에 섞임
        self.bias_estimate += learning_rate * drift  # ❌ 오염
```

### 개선된 구조 (Place Cells 통합)

```python
class Grid5DEngine:
    def __init__(self):
        # Place Cell Manager 추가
        self.place_manager = PlaceCellManager(num_places=1000)
    
    def update(self, current_state: np.ndarray):
        # 현재 위상 벡터에서 Place ID 추출
        phase_vector = self.state.get_phase_vector()  # (phi_x, phi_y, phi_z, phi_a, phi_b)
        place_id = self.place_manager.get_place_id(phase_vector)
        
        # Place별 독립적인 bias 업데이트
        place_memory = self.place_manager.get_place_memory(place_id)
        drift = current_state - target_state
        place_memory.update_bias(drift, learning_rate=0.1)
    
    def provide_reference(self, current_state: np.ndarray = None) -> np.ndarray:
        # 현재 위상 벡터에서 Place ID 추출
        phase_vector = self.state.get_phase_vector()
        place_id = self.place_manager.get_place_id(phase_vector)
        
        # Place별 bias 추정값 반환
        place_memory = self.place_manager.get_place_memory(place_id)
        return -place_memory.bias_estimate  # 보정 방향 (역방향)
```

---

## 📐 위상 공간 해상도

### 위상 공간 양자화

위상 공간을 이산화하여 Place ID를 생성할 때, 해상도를 설정해야 합니다:

\[
\Delta \phi = \frac{2\pi}{K}
\]

여기서:
- $\Delta \phi$: 위상 공간 해상도 (rad)
- $K$: 각 차원당 양자화 레벨 (예: 100)

**예시**: 5D 위상 공간에서 $K=100$이면
- 총 Place 수: $N = 100^5 = 10^{10}$ (너무 큼)
- 해싱을 사용하면: $N = 1000$ (관리 가능)

### 거리 측정 (Torus 거리)

위상 공간은 토러스($\mathbb{T}^n$)이므로, 거리 측정 시 wrapping을 고려해야 합니다:

\[
d(\Phi_1, \Phi_2) = \sqrt{\sum_{i=1}^{n} \min(\|\phi_{1,i} - \phi_{2,i}\|, 2\pi - \|\phi_{1,i} - \phi_{2,i}\|)^2}
\]

**구현 예시**:
```python
def torus_distance(
    phase1: np.ndarray,
    phase2: np.ndarray,
    phase_wrap: float = 2.0 * np.pi
) -> float:
    """토러스 거리 계산"""
    diff = phase1 - phase2
    # Wrapping: [-π, π] 범위로 정규화
    diff = diff - phase_wrap * np.round(diff / phase_wrap)
    distance = np.linalg.norm(diff)
    return distance
```

---

## 🔄 Place Field 학습

### 1. 초기 Place Field 생성

처음 방문한 위상 벡터를 Place Field 중심으로 설정:

\[
\Phi_i^{\text{new}} = \Phi_{\text{current}}
\]

### 2. Place Field 업데이트

동일 Place ID를 방문할 때마다 Place Field 중심을 업데이트:

\[
\Phi_i^{\text{new}} = \alpha \cdot \Phi_{\text{current}} + (1-\alpha) \cdot \Phi_i^{\text{old}}
\]

여기서:
- $\alpha$: 중심 업데이트 학습률 (예: 0.05)

### 3. Place Field 병합

두 Place Field가 너무 가까우면 병합:

\[
\text{if } \|\Phi_i - \Phi_j\| < r_{\text{merge}}: \text{merge}(i, j)
\]

여기서:
- $r_{\text{merge}}$: 병합 임계 거리 (예: $0.1$ rad)

---

## 📊 성능 고려사항

### 1. 메모리 사용량

각 Place Memory는 다음을 저장:
- `bias_estimate`: 5차원 벡터 (20 bytes)
- `visit_count`: 정수 (8 bytes)
- `last_visit_time`: float (8 bytes)
- `stable_state_snapshot`: Grid5DState (약 200 bytes)

**총 메모리**: 약 240 bytes/Place × 1000 Places = 240 KB (관리 가능)

### 2. 계산 복잡도

- **Place ID 할당**: $O(d)$ (d = 차원 수, 5D)
- **Bias 업데이트**: $O(d)$
- **Bias 조회**: $O(1)$ (해시 테이블)

**전체 복잡도**: $O(d)$ per update (기존과 동일)

### 3. 해싱 충돌 처리

해싱을 사용하면 충돌이 발생할 수 있습니다. 충돌 시:

1. **체이닝**: 같은 Place ID에 여러 Place Memory 저장 (연결 리스트)
2. **리니어 프로빙**: 다음 빈 슬롯 찾기
3. **재해싱**: 다른 해시 함수 사용

**권장**: 체이닝 방식 (구현 단순)

---

## 🎯 구현 단계

### 1단계: PlaceCellManager 기본 구조

```python
class PlaceCellManager:
    def __init__(self, num_places: int = 1000):
        self.num_places = num_places
        self.place_memory: Dict[int, PlaceMemory] = {}
    
    def get_place_id(self, phase_vector: np.ndarray) -> int:
        """위상 벡터를 Place ID로 변환"""
        pass
    
    def get_place_memory(self, place_id: int) -> PlaceMemory:
        """Place Memory 반환 (없으면 생성)"""
        pass
```

### 2단계: Place ID 할당 알고리즘

- 해싱 기반 구현
- 위상 공간 양자화

### 3단계: Place Memory 저장 구조

- `PlaceMemory` 데이터 클래스
- Bias 업데이트 로직

### 4단계: Grid5DEngine 통합

- `update()` 메서드에 Place ID 추출
- Place별 bias 업데이트
- `provide_reference()`에서 Place별 bias 반환

---

## 📝 참고 문헌

- O'Keefe & Nadel (1978). "The Hippocampus as a Cognitive Map"
- Moser et al. (2008). "Place cells, grid cells, and the brain's spatial representation system"
- Grid Engine 아키텍처: `docs/GRID_ENGINE_ARCHITECTURE.md`
- 해마 완성 로드맵: `docs/HIPPOCAMPUS_COMPLETION_ROADMAP.md`

---

**Last Updated**: 2026-01-20  
**Status**: 개념 정리 완료, 구현 준비 중


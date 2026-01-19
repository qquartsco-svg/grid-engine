"""
Context 분리(메모리 오염 방지) 벤치마크 (Context Split Benchmark)

목적:
- 동일 Place에서 Context가 달라질 때, bias 학습이 서로 오염되지 않는지 검증

시나리오:
1) 동일 Place A에서 Context=tool_A로 여러 번 접근/안정 구간 기록
2) 휴지기(Replay)로 tool_A bias를 Consolidation
3) 동일 Place A에서 Context=tool_B로 접근/안정 구간 기록
4) 휴지기(Replay)로 tool_B bias를 Consolidation
5) 다시 tool_A로 재방문 시 tool_A bias가 유지되는지 확인 (오염되면 실패)

비교군:
- Context Binder OFF (use_context_binder=False): 오염 발생 가능
- Context Binder ON  (use_context_binder=True): 오염 억제 기대

Author: GNJz
Created: 2026-01-20
Made in GNJz
License: MIT License
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import warnings
import logging

from grid_engine.dimensions.dim5d import Grid5DEngine, Grid5DConfig

warnings.filterwarnings("ignore")
logging.getLogger("matplotlib").setLevel(logging.ERROR)


def simulate_stable_visits(engine: Grid5DEngine, target: np.ndarray, n_steps: int, external_state: Dict) -> List[float]:
    """안정 구간을 만드는 간단 시뮬레이션: target 주변 미세 노이즈만 주입"""
    errors: List[float] = []
    for _ in range(n_steps):
        current = target + np.random.normal(0, 1e-4, 5)
        engine.set_external_state(external_state)
        engine.update(current)
        corr = engine.provide_reference()
        errors.append(float(np.linalg.norm(corr)))
    return errors


def idle_replay(engine: Grid5DEngine, target: np.ndarray, idle_ms: float = 2500.0):
    """휴지기(Replay) 트리거용 시간 점프 + update 1회"""
    engine.state.t_ms += idle_ms
    engine.update(target)


def main():
    print("\n" + "=" * 70)
    print("Context Split Benchmark (동일 Place, 다른 Context 메모리 오염 검증)")
    print("=" * 70)

    A = np.array([1.0, 0.5, 0.3, 10.0, 5.0])

    def run_case(use_context: bool) -> Tuple[float, float]:
        eng = Grid5DEngine(
            config=Grid5DConfig(),
            initial_x=A[0],
            initial_y=A[1],
            initial_z=A[2],
            initial_theta_a=A[3],
            initial_theta_b=A[4],
        )
        eng.set_target(A)
        eng.use_place_cells = True
        eng.use_context_binder = use_context
        if hasattr(eng, "replay_enabled"):
            eng.replay_enabled = True

        # tool_A 학습
        simulate_stable_visits(eng, A, 50, {"tool": "A", "temp": 20.0})
        idle_replay(eng, A)

        # tool_B 학습
        simulate_stable_visits(eng, A, 50, {"tool": "B", "temp": 20.0})
        idle_replay(eng, A)

        # tool_A 재방문 시 reference_correction norm
        errs = simulate_stable_visits(eng, A, 30, {"tool": "A", "temp": 20.0})
        return float(np.mean(errs)), float(np.std(errs))

    mean_off, std_off = run_case(use_context=False)
    mean_on, std_on = run_case(use_context=True)

    print("\n" + "=" * 70)
    print("결과 (tool_A 재방문 시 reference_correction norm)")
    print("=" * 70)
    print(f"{'조건':<24} {'mean(|corr|)':>14} {'std(|corr|)':>14}")
    print("-" * 56)
    print(f"{'Context OFF':<24} {mean_off:>14.6f} {std_off:>14.6f}")
    print(f"{'Context ON':<24}  {mean_on:>14.6f} {std_on:>14.6f}")
    print()

    print("실행:")
    print("  python3 benchmarks/context_split_test.py")
    print()


if __name__ == "__main__":
    main()



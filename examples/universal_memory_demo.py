"""
Universal Memory Demo
범용 기억 메모리 사용 예시

해마 메모리를 어떤 시스템에도 붙일 수 있는 범용 모듈로 사용하는 예시

Author: GNJz
Created: 2026-01-20
Made in GNJz
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from grid_engine.hippocampus.universal_memory import UniversalMemory, create_universal_memory


def demo_llm_integration():
    """LLM 통합 예시"""
    print("\n" + "=" * 70)
    print("예시 1: LLM 통합")
    print("=" * 70)
    
    # 범용 메모리 생성
    memory = create_universal_memory(memory_dim=5)
    
    # 대화 내용을 상태로 저장
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
    
    print(f"Query: {query}")
    print(f"Augmented Context: {augmented_context['summary']}")
    print(f"Memories: {len(augmented_context['memories'])}개")
    
    # LLM이 사용할 수 있는 컨텍스트
    llm_context = {
        "user_tendency": "이 사용자는 항상 조금 느리게 반응하는 경향이 있습니다.",
        "recommendation": "천천히 설명하는 것이 좋습니다."
    }
    print(f"LLM Context: {llm_context}")


def demo_control_system_integration():
    """제어 시스템 통합 예시"""
    print("\n" + "=" * 70)
    print("예시 2: 제어 시스템 통합")
    print("=" * 70)
    
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
    
    print(f"Position: {query_position}")
    print(f"Retrieved Memories: {len(memories)}개")
    for mem in memories:
        print(f"  - Type: {mem['type']}, Bias: {mem['bias']}, Confidence: {mem['confidence']:.2f}")
    
    # 제어 시스템이 사용할 수 있는 보정값
    correction = -memories[0]['bias']
    print(f"Control Correction: {correction}")


def demo_recommendation_system_integration():
    """추천 시스템 통합 예시"""
    print("\n" + "=" * 70)
    print("예시 3: 추천 시스템 통합")
    print("=" * 70)
    
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
    
    print(f"User State: {query_state}")
    print(f"Augmented Context: {augmented_context['summary']}")
    
    # 추천 시스템이 사용할 수 있는 정보
    recommendation_context = {
        "user_tendency": "이 사용자는 저녁 시간대에 모바일에서 이런 경향을 보입니다.",
        "recommendation": "비슷한 패턴의 콘텐츠를 추천하세요."
    }
    print(f"Recommendation Context: {recommendation_context}")


def demo_game_ai_integration():
    """게임 AI 통합 예시"""
    print("\n" + "=" * 70)
    print("예시 4: 게임 AI 통합")
    print("=" * 70)
    
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
    
    print(f"NPC Position: {query_position}")
    print(f"Retrieved Memories: {len(memories)}개")
    
    # 게임 AI가 사용할 수 있는 행동 보정
    behavior_correction = memories[0]['bias']
    print(f"Behavior Correction: {behavior_correction}")
    print("→ NPC가 이 위치에서 미묘하게 다른 행동을 보입니다.")


def main():
    """메인 함수"""
    print("\n" + "=" * 70)
    print("Universal Memory Demo")
    print("해마 메모리를 어떤 시스템에도 붙일 수 있는 범용 모듈로 사용")
    print("=" * 70)
    
    # 예시 실행
    demo_llm_integration()
    demo_control_system_integration()
    demo_recommendation_system_integration()
    demo_game_ai_integration()
    
    print("\n" + "=" * 70)
    print("Demo 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()


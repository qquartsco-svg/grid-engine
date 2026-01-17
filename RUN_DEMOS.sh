#!/bin/bash
#
# Grid Engine 데모 실행 스크립트
#
# 사용법:
#   ./RUN_DEMOS.sh              # 기본 데모 실행
#   ./RUN_DEMOS.sh basic        # 기본 데모만
#   ./RUN_DEMOS.sh visual       # 시각화 데모만
#   ./RUN_DEMOS.sh all          # 모든 데모 실행
#
# Author: [작성자 시그니처]
# Created: 2026-01

set -e  # 오류 발생 시 중단

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

echo "============================================================"
echo "Grid Engine 데모 실행"
echo "============================================================"
echo ""

# 데모 파일 확인
DEMO_BASIC="examples/run_grid_basic_demo.py"
DEMO_VISUAL="examples/run_grid_visual_demo.py"

# 실행할 데모 선택
if [ "$1" == "basic" ]; then
    DEMOS=("$DEMO_BASIC")
elif [ "$1" == "visual" ]; then
    DEMOS=("$DEMO_VISUAL")
elif [ "$1" == "all" ] || [ -z "$1" ]; then
    DEMOS=("$DEMO_BASIC" "$DEMO_VISUAL")
else
    echo "❌ 잘못된 인자: $1"
    echo "사용법: ./RUN_DEMOS.sh [basic|visual|all]"
    exit 1
fi

# 데모 실행
for demo in "${DEMOS[@]}"; do
    if [ ! -f "$demo" ]; then
        echo "⚠️  데모 파일을 찾을 수 없습니다: $demo"
        continue
    fi
    
    echo "============================================================"
    echo "실행: $demo"
    echo "============================================================"
    echo ""
    
    python3 "$demo"
    
    echo ""
    echo ""
done

echo "============================================================"
echo "데모 실행 완료!"
echo "============================================================"


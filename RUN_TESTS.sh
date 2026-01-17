#!/bin/bash
#
# Grid Engine 테스트 실행 스크립트
#
# 사용법:
#   ./RUN_TESTS.sh          # 모든 테스트 실행
#   ./RUN_TESTS.sh -v       # 상세 출력
#   ./RUN_TESTS.sh -k test_name  # 특정 테스트만 실행
#
# Author: [작성자 시그니처]
# Created: 2026-01

set -e  # 오류 발생 시 중단

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

echo "============================================================"
echo "Grid Engine 테스트 실행"
echo "============================================================"
echo ""

# pytest 설치 확인
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "⚠️  pytest가 설치되어 있지 않습니다."
    echo "설치 중: pip install pytest"
    pip install pytest -q
    echo ""
fi

# 테스트 실행
echo "테스트 디렉토리: tests/"
echo "테스트 파일:"
ls -1 tests/*.py 2>/dev/null | sed 's/^/  - /'
echo ""

# pytest 실행
if [ "$1" == "-v" ]; then
    python3 -m pytest tests/ -v
elif [ "$1" == "-k" ] && [ -n "$2" ]; then
    python3 -m pytest tests/ -v -k "$2"
else
    python3 -m pytest tests/ -v --tb=short
fi

echo ""
echo "============================================================"
echo "테스트 완료!"
echo "============================================================"


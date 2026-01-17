#!/bin/bash
# Grid Engine v0.1.1 - GitHub 업로드 스크립트

echo "=========================================="
echo "Grid Engine v0.1.1 - GitHub 업로드"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
if [ ! -d ".git" ]; then
    echo "❌ 오류: Git 저장소가 아닙니다."
    exit 1
fi

# 원격 저장소 확인
if ! git remote | grep -q origin; then
    echo "원격 저장소 설정 중..."
    git remote add origin https://github.com/qquartsco-svg/grid-engine.git
fi

# 브랜치 이름 확인
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "브랜치 이름을 main으로 변경 중..."
    git branch -M main
fi

# 커밋 확인
if [ -z "$(git log --oneline -1 2>/dev/null)" ]; then
    echo "❌ 오류: 커밋이 없습니다."
    exit 1
fi

echo "✅ 현재 상태:"
echo "   커밋: $(git log --oneline -1 | cut -d' ' -f1)"
echo "   브랜치: $(git branch --show-current)"
echo "   원격 저장소: $(git remote get-url origin)"
echo ""

# 사용자 확인
read -p "GitHub에 업로드하시겠습니까? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "업로드 취소됨"
    exit 0
fi

# 푸시
echo ""
echo "📤 GitHub에 푸시 중..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ 푸시 완료!"
else
    echo "❌ 푸시 실패. GitHub 레포지토리가 생성되었는지 확인하세요."
    echo ""
    echo "GitHub 레포지토리 생성:"
    echo "  https://github.com/new"
    echo "  Repository name: grid-engine"
    echo "  Owner: qquartsco-svg"
    exit 1
fi

# 태그 푸시
echo ""
echo "📤 태그 푸시 중..."
git push origin v0.1.1

if [ $? -eq 0 ]; then
    echo "✅ 태그 푸시 완료!"
else
    echo "⚠️  태그 푸시 실패 (태그가 없을 수 있음)"
fi

echo ""
echo "=========================================="
echo "업로드 완료!"
echo "=========================================="
echo ""
echo "레포지토리: https://github.com/qquartsco-svg/grid-engine"
echo "태그: v0.1.1"
echo ""


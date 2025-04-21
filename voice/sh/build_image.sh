#!/bin/bash
  
# 이미지 이름과 레지스트리 인자값
REGISTRY=${1:-"$AWS_ECR"}  # 기본값은 AWS_ECR 환경 변수
IMAGE_NAME="${REGISTRY}/voice:1"

# Docker 이미지 빌드
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "Docker 이미지 '$IMAGE_NAME'가 성공적으로 빌드되었습니다."
else
    echo "Docker 이미지 빌드 중 오류 발생."
    exit 1
fi

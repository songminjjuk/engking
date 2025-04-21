#!/bin/bash

# 인자로 받은 레지스트리 주소 또는 AWS_ECR 환경 변수
REGISTRY=${1:-"$AWS_ECR"}

# 이미지 이름
IMAGE_NAME="voice:1"

# 레지스트리에 로그인 (필요한 경우)
# docker login $REGISTRY

# 이미지 푸시
docker tag $IMAGE_NAME $REGISTRY/$IMAGE_NAME
docker push $REGISTRY/$IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "Docker 이미지 '$IMAGE_NAME'가 '$REGISTRY'에 성공적으로 푸시되었습니다."
else
    echo "Docker 이미지 푸시 중 오류 발생."
    exit 1
fi

#!/bin/bash

# .env 파일에서 환경 변수 로드
export $(grep -v '^#' .env | xargs)

# 파일 업로드
aws s3 cp audio.mp3 s3://$BUCKET_NAME/audio.mp3 --region $AWS_REGION

# 업로드 결과 확인
if [ $? -eq 0 ]; then
    echo "File uploaded successfully: s3://$BUCKET_NAME/audio.mp3"
else
    echo "File upload failed."
fi

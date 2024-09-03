#!/bin/bash

# .env 파일에서 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME을 읽어옵니다.
export $(grep -E 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|BUCKET_NAME' .env)

# S3 버킷 삭제 (비어있지 않은 버킷은 먼저 객체를 삭제해야 함)
echo "Deleting all objects in bucket $BUCKET_NAME..."

# 버킷 내 모든 객체 삭제
aws s3 rm "s3://$BUCKET_NAME" --recursive

# 버킷 삭제
aws s3api delete-bucket --bucket "$BUCKET_NAME"

echo "S3 bucket $BUCKET_NAME has been successfully deleted."

# app/utils/config.py

import os

# 환경 변수에서 필요한 값을 가져오거나 기본값 설정
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "mmmybucckeet")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REGION_NAME = os.getenv("REGION_NAME", "ap-northeast-1")
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
# ROLE_ARN = os.getenv("ROLE_ARN", "your-role-arn")

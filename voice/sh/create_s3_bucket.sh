#!/bin/bash

# .env 파일에서 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, AWS_REGION을 읽어옵니다.
set -o allexport
source .env
set +o allexport

# S3 버킷 생성
aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION" --create-bucket-configuration LocationConstraint="$AWS_REGION"

# CORS 설정 적용
cat <<EOF > cors.json
{
    "CORSRules": [
        {
            "AllowedHeaders": [
                "*"
            ],
            "AllowedMethods": [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "HEAD"
            ],
            "AllowedOrigins": [
                "*"
            ],
            "ExposeHeaders": [
                "x-amz-server-side-encryption",
                "x-amz-request-id",
                "x-amz-id-2"
            ],
            "MaxAgeSeconds": 3000
        }
    ]
}
EOF

aws s3api put-bucket-cors --bucket "$BUCKET_NAME" --cors-configuration file://cors.json

# 버킷 정책 설정 (모든 IAM 유저 허용)
cat <<EOL > policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOL

aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy file://policy.json

# 퍼블릭 액세스 차단 해제
aws s3api put-public-access-block --bucket "$BUCKET_NAME" --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# 정리
rm cors.json
rm policy.json

echo "S3 bucket $BUCKET_NAME has been successfully created and configured with public access."

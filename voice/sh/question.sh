#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Define S3 bucket and object details
bucket_name="$BUCKET_NAME"  # S3 버킷 이름을 .env 파일에서 불러옴
memberId="1234"
chatRoomId="1234_2024-09-04T01:43:14"
messageId="1"
audioFileName="${memberId}/${chatRoomId}/${messageId}.mp3"

# # S3 객체 삭제
# echo "=============================="
# echo "1. Deleting existing S3 object if it exists..."
# aws s3 rm "s3://${bucket_name}/audio/${audioFileName}"

# First question generation request
echo "=============================="
echo "2. Sending first question generation request..."
response=$(curl -s -X POST "http://${API_HOST}:8000/api/first-question/" \
-H "Content-Type: application/json" \
-d '{
  "memberId": "'"$memberId"'",
  "topic": "coffee",
  "difficulty": "easy"
}')

# Print and parse the response
echo "응답1:"
echo "$response" | jq .

# Validate and extract values from the response
memberId=$(echo "$response" | jq -r '.memberId // empty')
chatRoomId=$(echo "$response" | jq -r '.chatRoomId // empty')
messageId=$(echo "$response" | jq -r '.messageId // empty')

if [ -z "$memberId" ] || [ -z "$chatRoomId" ] || [ -z "$messageId" ]; then
    echo "Error: Missing essential fields in the response. Please check the API response."
    exit 1
fi

messageId=$((messageId + 1))

audioFileName="${memberId}/${chatRoomId}/${messageId}.mp3"

# S3 객체 삭제 (presigned URL 생성 전에)
echo "=============================="
echo "3. Deleting existing S3 object again before creating presigned URL..."
aws s3 rm "s3://${bucket_name}/audio/${audioFileName}"

# Get presigned URL
echo "=============================="
echo "4. Requesting presigned URL..."
presigned_response=$(curl -s -X POST "http://${API_HOST}:8000/api/create-put-url/" \
-H "Content-Type: application/json" \
-d '{
  "filename": "'"$audioFileName"'"
}')

# Extract the presigned URL
presignedUrl=$(echo "$presigned_response" | jq -r '.presignedUrl')

echo $presignedUrl

# Validate the presigned URL
if [ -z "$presignedUrl" ]; then
    echo "Error: Failed to obtain presigned URL. Please check the response."
    echo "$presigned_response" | jq .
    exit 1
fi

# Print the presigned URL
echo "Presigned URL: $presignedUrl"

# Upload audio file to presigned URL
echo "=============================="
echo "5. Uploading audio file to presigned URL..."
cp sh/audio.mp3 temp_audio.mp3  # 로컬에서 sh/audio.mp3 파일 복제

# 파일을 업로드합니다.
python sh/put.py $presignedUrl temp_audio.mp3

# Clean up temporary files
rm temp_audio.mp3

# Second question processing request
echo "=============================="
echo "6. Sending second question processing request..."

response2=$(curl -s -X POST "http://${API_HOST}:8000/api/next-question/" \
-H "Content-Type: application/json" \
-d '{
  "memberId": "'"$memberId"'",
  "chatRoomId": "'"$chatRoomId"'",
  "messageId": "'"$messageId"'",
  "filename": "'"$audioFileName"'",
  "topic": "coffee",
  "difficulty": "easy"
}')

# Print and validate the response
echo "응답2:"
echo "$response2"

# Check if messageId is empty
messageId=$(echo "$response2" | jq -r '.messageId')
messageId=$((messageId + 1))

# 피드백 요청 처리
echo "=============================="
echo "7. Sending feedback request..."
feedback_response=$(curl -s -X POST "http://${API_HOST}:8000/api/feedback/" \
-H "Content-Type: application/json" \
-d '{
  "memberId": "'"$memberId"'",
  "chatRoomId": "'"$chatRoomId"'",
  "messageId": "'"$messageId"'",
  "responseText": "Great question!"
}')

# Print the feedback response
echo "피드백 응답:"
echo "$feedback_response".

# Validate JSON structure of the feedback response
echo "=============================="
echo "피드백 응답 JSON 구조:"
echo "$feedback_response" | jq .

echo -e "\nRequest completed."

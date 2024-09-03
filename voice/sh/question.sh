#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# First question generation request
echo "Sending first question generation request..."
response=$(curl -s -X POST "http://${API_HOST}:8000/api/first-question/" \
-H "Content-Type: application/json" \
-d '{
  "memberId": "1234",
  "topic": "coffee",
  "difficulty": "easy"
}')

# Print the response
echo "응답1:"
echo "$response"

# Extract values from the response using jq
memberId=$(echo "$response" | jq -r '.memberId')
chatRoomId=$(echo "$response" | jq -r '.chatRoomId')
messageId=$(echo "$response" | jq -r '.messageId')
audioFileName="${memberId}/${chatRoomId}/${messageId}.mp3"

# Get presigned URL
echo "Requesting presigned URL..."
presigned_response=$(curl -s -X POST "http://${API_HOST}:8000/api/create-put-url/" \
-H "Content-Type: application/json" \
-d '{
  "filename": "'"$audioFileName"'"
}')

echo $audioFileName

# Extract the presigned URL
presignedUrl=$(echo "$presigned_response" | jq -r '.presignedUrl')

# Upload audio file to presigned URL
echo "Uploading audio file to presigned URL..."
echo $presignedUrl

cp sh/audio.mp3 temp_audio.mp3  # 로컬에서 sh/audio.mp3 파일 복제
curl -X PUT "$presignedUrl" \
-H "Content-Type: audio/mpeg" \
--data-binary @temp_audio.mp3

# Clean up temporary file
rm temp_audio.mp3

# Second question processing request
echo "Sending second question processing request..."
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

# Print the response
echo "응답2:"
echo "$response2"

echo -e "\nRequest completed."

# 피드백 요청 처리
echo "Sending feedback request..."
messageId="2"

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
echo "$feedback_response"

# 응답의 JSON 구조 확인
echo "$feedback_response" | jq .

echo -e "\nRequest completed."


#!/bin/bash

# 업로드할 오디오 파일의 경로
audioFilePath="sh/audio.mp3"

# memberId를 설정합니다. (여기에 실제 값을 입력하세요)
memberId="1234"
chatRoomId="1234_2024-09-02T00:00:00"

# 현재 시각을 HHMM 형식으로 가져와서 messageId로 설정
messageId=$(date +%H%M)  # ex) 1727
audioFileName="${memberId}/${chatRoomId}/${messageId}.mp3"

echo $audioFileName
# Get presigned URL
echo "Requesting presigned URL..."
presigned_response=$(curl -s -X POST "http://127.0.0.1:8000/api/create-put-url/" \
-H "Content-Type: application/json" \
-d '{
  "filename": "'"$audioFileName"'"
}')

# Extract the presigned URL
presignedUrl=$(echo "$presigned_response" | jq -r '.presignedUrl')

echo $presignedUrl

# 업로드할 오디오 파일이 존재하는지 확인
if [[ ! -f "$audioFilePath" ]]; then
  echo "오디오 파일이 존재하지 않습니다: $audioFilePath"
  exit 1
fi

# Upload audio file to presigned URL
echo "Uploading audio file to presigned URL..."
curl -X PUT "$presignedUrl" \
-H "Content-Type: audio/mpeg" \
--data-binary @"$audioFilePath"

echo "업로드가 완료되었습니다."

# 피드백 요청 처리 (필요 시 추가)

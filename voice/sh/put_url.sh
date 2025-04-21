#!/bin/bash

# .env 파일을 읽어오기
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# AWS 키 확인
# echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
# echo "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"

# 업로드할 오디오 파일의 경로
audioFilePath="sh/audio.mp3"

# memberId를 설정합니다. (여기에 실제 값을 입력하세요)
memberId="1234"
chatRoomId="1234_2024-09-02T00:00:00"

# 현재 시각을 HHMM 형식으로 가져와서 messageId로 설정
messageId="test"

audioFileName="${memberId}/${chatRoomId}/${messageId}.mp3"

# S3 업로드 로그 파일 경로
LOG_FILE="upload_log.txt"

echo $audioFileName

# Check AWS keys
check_aws_keys() {
  if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "AWS 키가 설정되어 있지 않습니다."
    echo "AWS 키가 설정되어 있지 않습니다." >> "$LOG_FILE"
    exit 1
  fi
}

# Check system time
check_system_time() {
  current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "현재 UTC 시간: $current_time"
}

# Get presigned URL
echo "Requesting presigned URL..."
presigned_response=$(curl -s -X POST "http://127.0.0.1:8000/api/create-put-url/" \
-H "Content-Type: application/json" \
-d '{
  "filename": "'"$audioFileName"'"
}')

# Extract the presigned URL
presignedUrl=$(echo "$presigned_response" | jq -r '.presignedUrl')

echo 'pu:'
echo $presignedUrl

# 업로드할 오디오 파일이 존재하는지 확인
if [[ ! -f "$audioFilePath" ]]; then
  echo "오디오 파일이 존재하지 않습니다: $audioFilePath"
  echo "오디오 파일이 존재하지 않습니다: $audioFilePath" >> "$LOG_FILE"
  exit 1
fi

# AWS 키 및 시스템 시간 체크
check_aws_keys
check_system_time

echo "Uploading file..."

# 파일을 업로드합니다.
python3 sh/put.py $presignedUrl $audioFilePath

# upload_response=$(curl -L -v -X PUT \
# # -H "Content-Type: audio/mpeg" \
# --upload-file "$audioFilePath" "$presignedUrl" 2>&1)

# # 업로드 응답을 로그 파일에 기록
# echo "$upload_response" >> "$LOG_FILE"

# # 업로드 성공 여부 확인
# if [[ "$upload_response" == *"200 OK"* || "$upload_response" == *"201 Created"* ]]; then
#   echo "파일 업로드 성공"
#   echo "파일 업로드 성공: $audioFileName" >> "$LOG_FILE"
# else
#   echo "파일 업로드 실패"
#   echo "파일 업로드 실패: $audioFileName" >> "$LOG_FILE"

#   # 로그 파일에서 에러 메시지 추출
#   ERROR_CODE=$(echo "$upload_response" | grep '<Code>' | sed 's/.*<Code>\(.*\)<\/Code>/\1/')
#   ERROR_MESSAGE=$(echo "$upload_response" | grep '<Message>' | sed 's/.*<Message>\(.*\)<\/Message>/\1/')
#   REQUEST_ID=$(echo "$upload_response" | grep '<RequestId>' | sed 's/.*<RequestId>\(.*\)<\/RequestId>/\1/')
#   HOST_ID=$(echo "$upload_response" | grep '<HostId>' | sed 's/.*<HostId>\(.*\)<\/HostId>/\1/')

#   # 에러 메시지 출력
#   echo "에러 코드: $ERROR_CODE"
#   echo "에러 메시지: $ERROR_MESSAGE"
#   echo "요청 ID: $REQUEST_ID"
#   echo "호스트 ID: $HOST_ID"

#   # 추가적인 정보 제공
#   if [[ "$ERROR_CODE" == "SignatureDoesNotMatch" ]]; then
#       echo "문제 해결을 위한 조치:"
#       echo "- AWS 키와 서명 방법을 확인하세요."
#       echo "- 요청 URL과 헤더를 다시 검토하세요."
#       echo "- 시스템 시간이 올바른지 확인하세요."
#   fi
# fi

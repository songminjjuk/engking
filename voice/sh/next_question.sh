#!/bin/bash

# .env 파일에서 환경 변수 로드
export $(grep -v '^#' .env | xargs)

# JSON 페이로드 설정
json_payload='{
  "memberId": "1006",
  "chatRoomId": "1006_2024-09-02T09:50:45",
  "messageId": "2",
  "messageText": "I think I’ll go with a latte today. I love how creamy and smooth it is!",
  "topic": "coffee",
  "difficulty": "Normal"
}'

# 다음 질문 요청
echo "다음 질문 요청 전송..."
response=$(curl -s -X POST "$B3_URL/chat/nextquestion" \
-H "Content-Type: application/json" \
-d "$json_payload")

# 응답 출력
echo "응답:"
echo "$response"

echo "응답 json:"
# 응답의 JSON 구조 확인
echo "$response" | jq .

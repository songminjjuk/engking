#!/bin/bash

# .env 파일에서 환경 변수 로드
export $(grep -v '^#' .env | xargs)

# 테스트할 변수 설정
MEMBER_ID="1234"
TOPIC="coffee"
DIFFICULTY="easy"

# 첫 번째 질문 요청
echo "첫 번째 질문 요청 전송..."
response=$(curl -s -X POST "$B3_URL/chat/firstquestion" \
-H "Content-Type: application/json" \
-d '{
  "memberId": "'"$MEMBER_ID"'",
  "topic": "'"$TOPIC"'",
  "difficulty": "'"$DIFFICULTY"'"
}')

# 응답 출력
echo "첫 번째 질문 응답:"
echo "$response"

# 첫 번째 질문 응답에서 messageId와 chatRoomId 추출
MESSAGE_ID=$(echo "$response" | jq -r '.messageId')
CHAT_ROOM_ID=$(echo "$response" | jq -r '.chatRoomId')

# 종료 질문 요청
echo "종료 질문 요청 전송..."
end_response=$(curl -s -X POST "$B3_URL/chat/endquestion" \
-H "Content-Type: application/json" \
-d '{
  "memberId": "'"$MEMBER_ID"'",
  "chatRoomId": "'"$CHAT_ROOM_ID"'",
  "messageId": "'"$MESSAGE_ID"'",
  "endRequest": true
}')

# 응답 출력
echo "종료 질문 응답:"
echo "$end_response"

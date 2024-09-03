import os
import requests
import json

def get_next_question(member_id: str, chat_room_id: str, message_id: str, message_text: str, topic: str, difficulty: str):
  b3_url = os.getenv('B3_URL')

  # 요청 본문 생성
  request_body = {
      "memberId": member_id,
      "chatRoomId": chat_room_id,
      "messageId": message_id,
      "messageText": message_text,
      "topic": topic,
      "difficulty": difficulty
  }

  # POST 요청 보내기
  try:
      response = requests.post(
          f"{b3_url}/chat/nextquestion",
          headers={"Content-Type": "application/json"},
          data=json.dumps(request_body)
      )

      # 응답 처리
      if response.status_code == 200:
          response_data = response.json()

          return {
              "success": response_data.get("success"),
              "nextQuestion": response_data.get("nextQuestion", "Temporary question"),
              "chatRoomId": response_data.get("chatRoomId"),
              "memberId": response_data.get("memberId"),
              "messageId": response_data.get("messageId"),
              "createdTime": response_data.get("createdTime")
          }
      elif response.status_code == 503:
          response_data = response.json()
          return {
              "success": response_data.get("success"),
              "memberId": response_data.get("memberId"),
              "chatRoomId": response_data.get("chatRoomId"),
              "createdTime": response_data.get("createdTime"),
              "message": "서비스가 이용 불가입니다. 나중에 다시 시도해주세요."
          }
      else:
          return {
              "success": False,
              "message": "잘못된 요청 형식입니다."
          }
  except Exception as e:
      return {
          "success": False,
          "message": str(e)
      }
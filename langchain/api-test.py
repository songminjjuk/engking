import requests

def stream_response(url, payload):
    # API에 POST 요청을 보내고 스트리밍 응답을 받습니다.
    response = requests.post(url, json=payload, stream=True, timeout=120)

    # 응답이 성공적인지 확인합니다.
    if response.status_code == 200:
        print(f"Streaming response from {url}:")
        # 응답을 스트리밍 방식으로 처리합니다.
        for chunk in response:
            print(chunk, end="")
    else:
        print(f"Failed to connect to {url}: {response.status_code}")

if __name__ == "__main__":
    # API의 URL (EC2의 퍼블릭 IP 또는 도메인으로 대체)
    base_url = "http://13.231.43.88:5000"

    # /chat 엔드포인트 테스트
    chat_url = f"{base_url}/chat"
    chat_payload = {
        "user_id": "test_user",
        "conversation_id": "conv1",
        "input": "Can you ask me a question?",
        "difficulty": "Normal",
        "scenario": "커피 주문하기"
    }
    stream_response(chat_url, chat_payload)

    print("\n\n")

    # /quiz 엔드포인트 테스트
    quiz_url = f"{base_url}/quiz"
    quiz_payload = {
        "user_id": "test_user",
        "conversation_id": "conv2",
        "quiz_type": "vocabulary",
        "difficulty": "Normal",
        "input": "Please give me a quiz question."
    }
    stream_response(quiz_url, quiz_payload)

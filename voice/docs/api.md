# api

## 엔드포인트

### Presigned URL 생성

- URL: `/api/create-put-url/`
- 메소드: POST
- 요청 본문:
  ```json
  {
    "filename": "string"
  }
  ```
- 응답:
  - 200 OK
    ```json
    {
      "success": true,
      "presignedUrl": "string"
    }
    ```

### First Question 생성

- URL: `/api/first-question`
- 메소드: POST
- 요청 본문:
  ```json
  {
    "memberId": "string",
    "topic": "string",
    "difficulty": "string"
  }
  ```
- 응답:
  - 200 OK
    ```json
    {
      "success": true,
      "firstQuestion": "string",
      "audioUrl": "string",
      "memberId": "string",
      "chatRoomId": "string",
      "messageId": "string"
    }
    ```

### Next Question 처리

- URL: `/api/next-question`
- 메소드: POST
- 요청 본문:
  ```json
  {
    "memberId": "string",
    "chatRoomId": "string",
    "messageId": "string"
  }
  ```
- 응답:
  - 200 OK
    ```json
    {
      "success": true,
      "nextQuestion": "string",
      "memberId": "string",
      "chatRoomId": "string",
      "audioUrl": "string"
    }
    ```

### 음성 저장 완료 알림 및 텍스트 변환

- URL: `/api/transcription`
- 메소드: POST
- 요청 본문:
  ```json
  {
    "memberId": "string",
    "chatRoomId": "string",
    "audioUrl": "string"
  }
  ```
- 응답:
  - 200 OK
    ```json
    {
      "success": true,
      "memberId": "string",
      "responseText": "string",
      "audioUrl": "string"
   
    }
    ```

### Answer 및 Feedback 처리

- **URL**: `/api/feedback`
- **메소드**: POST
- **요청 본문**:
  ```json
  {
    "memberId": "string",
    "chatRoomId": "string",
    "messageId": "string",
    "responseText": "string"
  }
  ```
- **응답**:
  - **200 OK**
    ```json
    {
      "success": true,
      "messageId": "string",
      "score": "string",
      "feedback": "string",
      "audioUrl": "string"
    }
    ```

## 오류 응답

- 400 Bad Request
  - 잘못된 요청 형식
  - 예시:
    ```json
    {
      "success": false,
      "message": "잘못된 요청 형식입니다."
    }
    ```
- 500 Internal Server Error
  - 서버 오류
  - 예시:
    ```json
    {
      "success": false,
      "message": "서버에서 오류가 발생했습니다."
    }
    ``` 
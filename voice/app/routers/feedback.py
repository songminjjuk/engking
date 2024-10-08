# app/routers/feedback.py
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator
from botocore.exceptions import BotoCoreError
from app.modules.end_question import get_end_question
from app.modules.polly import synthesize_speech
from app.modules.s3 import generate_presigned_url
from app.modules.common import generate_unique_filename
import time
from loguru import logger

router = APIRouter()

# 피드백 요청 모델
class FeedbackRequest(BaseModel):
    memberId: str
    chatRoomId: str
    messageId: str
    responseText: str

    @field_validator('memberId', 'chatRoomId', 'messageId', 'responseText')
    def check_not_empty(cls, value):
        if not value:
            raise ValueError('이 필드는 비어 있을 수 없습니다.')
        return value

# 피드백 응답 모델
class FeedbackResponse(BaseModel):
    success: bool
    messageId: str
    score: str
    feedback: str
    audioUrl: str

@router.post("/api/feedback/", response_model=FeedbackResponse)
async def handle_feedback(request: Request, body: FeedbackRequest):

    # 요청 시작 시각 기록
    start_time = time.time()

    try:
        # 요청 바디 데이터 기록
        data = await request.json()
        logger.info(f"Request received: method={request.method}, url={request.url}, data={data}")

        # 종료 질문 가져오기
        end_question_response = get_end_question(body.memberId, body.chatRoomId, body.messageId)

        # 피드백 처리 로직
        try:
            score = end_question_response['score']
            feedback = end_question_response['feedback']
            memberId = end_question_response['memberId']
            chatRoomId = end_question_response['chatRoomId']
            messageId = end_question_response['messageId']
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"응답 데이터에 '{e.args[0]}' 필드가 없습니다.")

        try:
            # 음성 파일 명 생성
            audio_filename = generate_unique_filename(
                memberId,
                chatRoomId,
                messageId)

            # 피드백을 음성으로 변환
            # 프리사인 URL 생성
            audio_presigned_url = synthesize_speech(feedback, audio_filename)

        except (BotoCoreError, Exception) as e:
            raise HTTPException(status_code=500, detail=f"음성 변환 중 오류 발생: {str(e)}")
        
        # 요청 처리 시간 기록
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # 밀리초로 변환

        # 응답 성공 로그 기록
        logger.info(f"Response successful: status=200, duration={duration:.2f}ms")

        return FeedbackResponse(
            success=True,
            messageId=messageId,
            score=score,
            feedback=feedback,
            audioUrl=audio_presigned_url  # audioUrl 포함
        )
    except HTTPException as e:
        # 요청 처리 시간 기록
        end_time = time.time()
        duration = (end_time - start_time) * 1000

        # 에러 발생 시 로그 기록 (한 줄로, 메시지만 포함)
        logger.error(f"HTTPException occurred: {str(e.detail)}, duration={duration:.2f}ms")

        # HTTP 예외 처리
        raise e
    except Exception as e:
        # 요청 처리 시간 기록
        end_time = time.time()
        duration = (end_time - start_time) * 1000

        # 에러 발생 시 로그 기록 (한 줄로, 메시지만 포함)
        logger.error(f"Exception occurred: {str(e)}, duration={duration:.2f}ms")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
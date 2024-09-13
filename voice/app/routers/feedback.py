import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from botocore.exceptions import BotoCoreError
from app.modules.end_question import get_end_question
from app.modules.polly import synthesize_speech
from app.modules.s3 import generate_presigned_url
from app.modules.common import generate_unique_filename

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
async def handle_feedback(request: FeedbackRequest):

    # 종료 질문 가져오기
    end_question_response = get_end_question(request.memberId, request.chatRoomId, request.messageId)

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

    return FeedbackResponse(
        success=True,
        messageId=messageId,
        score=score,
        feedback=feedback,
        audioUrl=audio_presigned_url  # audioUrl 포함
    )
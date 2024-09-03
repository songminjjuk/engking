import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from botocore.exceptions import BotoCoreError
from app.modules.end_question import get_end_question
from app.modules.polly import synthesize_speech
from app.modules.s3 import generate_presigned_url

router = APIRouter()

# 피드백 요청 모델
class FeedbackRequest(BaseModel):
    memberId: str
    chatRoomId: str
    messageId: str
    responseText: str

# 피드백 응답 모델
class FeedbackResponse(BaseModel):
    success: bool
    messageId: str
    score: str
    feedback: str
    audioUrl: str  # audioUrl 필드 추가

@router.post("/api/feedback/", response_model=FeedbackResponse)
async def handle_feedback(request: FeedbackRequest):
    
    # 종료 질문 가져오기
    end_question_response = get_end_question(request.memberId, request.chatRoomId, request.messageId)
    # if not end_question_response['success']:
    #     raise HTTPException(status_code=500, detail="종료 질문을 가져오는 중 오류 발생.")

    # 피드백 처리 로직
    score = end_question_response['score']
    feedback = end_question_response['feedback']
    messageId = end_question_response['messageId']

    try:
        # 음성 파일 명 생성
        audio_filename = f"{request.memberId}_{request.chatRoomId}_{messageId}.mp3"

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

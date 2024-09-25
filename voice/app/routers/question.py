import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from app.modules.first_question import get_first_question  # 질문 생성 함수 임포트
from app.modules.polly import synthesize_speech  # 음성 합성 함수 임포트
from app.modules.next_question import get_next_question  # 다음 질문 함수 임포트
from app.modules.transcribe import transcribe_audio
from app.modules.common import generate_unique_filename

router = APIRouter()

class FirstQuestionRequest(BaseModel):
    memberId: str
    topic: str
    difficulty: str

    @field_validator('memberId', 'topic', 'difficulty')
    def check_not_empty(cls, value):
        if not value:
            raise ValueError('이 필드는 비어 있을 수 없습니다.')
        return value

class FirstQuestionResponse(BaseModel):
    success: bool
    audioUrl: str
    firstQuestion: str
    memberId: str
    chatRoomId: str
    messageId: str

class NextQuestionRequest(BaseModel):
    memberId: str
    chatRoomId: str
    messageId: str
    filename: str
    topic: str
    difficulty: str

    @field_validator('memberId', 'chatRoomId', 'messageId', 'filename', 'topic', 'difficulty')
    def check_not_empty(cls, value):
        if not value:
            raise ValueError('이 필드는 비어 있을 수 없습니다.')
        return value

class NextQuestionResponse(BaseModel):
    success: bool
    nextQuestion: str
    memberId: str
    chatRoomId: str
    messageId: str
    audioUrl: str

@router.post("/api/first-question/", response_model=FirstQuestionResponse)
async def create_first_question(request: FirstQuestionRequest):
    # 질문 생성 로직 구현
    quiz_response = get_first_question(request.memberId, request.topic, request.difficulty)

    if not quiz_response['success']:
        raise HTTPException(status_code=500, detail="질문 생성에 실패했습니다.")

    # 고유한 파일명 생성
    audio_filename = generate_unique_filename(
        quiz_response['memberId'],
        quiz_response['chatRoomId'],
        quiz_response['messageId']
    )
    
    audio_url = synthesize_speech(quiz_response['firstQuestion'], audio_filename)

    return FirstQuestionResponse(
        success=quiz_response['success'],
        audioUrl=audio_url,
        firstQuestion=quiz_response['firstQuestion'],
        memberId=quiz_response['memberId'],
        chatRoomId=quiz_response['chatRoomId'],
        messageId=quiz_response['messageId']
    )

@router.post("/api/next-question/", response_model=NextQuestionResponse)
async def handle_next_question(request: NextQuestionRequest):
    messageText = await transcribe_audio(request.filename)

    # 다음 질문 처리 로직 구현
    next_question_response = get_next_question(
        request.memberId,
        request.chatRoomId,
        request.messageId,
        messageText,
        request.topic,
        request.difficulty
    )

    if not next_question_response['success']:
        raise HTTPException(status_code=500, detail="다음 질문 처리에 실패했습니다.")
    
    # 고유한 파일명 생성
    audio_filename = generate_unique_filename(
        next_question_response['memberId'],
        next_question_response['chatRoomId'],
        next_question_response['messageId']
    )
    audio_url = synthesize_speech(next_question_response['nextQuestion'], audio_filename)

    return NextQuestionResponse(
        success=next_question_response['success'],
        nextQuestion=next_question_response['nextQuestion'],
        memberId=next_question_response['memberId'],
        chatRoomId=next_question_response['chatRoomId'],
        messageId=next_question_response['messageId'],
        audioUrl=audio_url
    )

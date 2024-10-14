# app/routers/question.py
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator
from app.modules.first_question import get_first_question  # 질문 생성 함수 임포트
from app.modules.polly import synthesize_speech  # 음성 합성 함수 임포트
from app.modules.next_question import get_next_question  # 다음 질문 함수 임포트
from app.modules.transcribe import transcribe_audio
from app.modules.common import generate_unique_filename
import time
from loguru import logger

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
    messageText: str
    
@router.post("/api/first-question/", response_model=FirstQuestionResponse)
async def create_first_question(request: Request, body: FirstQuestionRequest):
    # 요청 시작 시각 기록
    start_time = time.time()

    try:
        # 요청 바디 데이터 기록
        data = await request.json()
        logger.info(f"Request received: method={request.method}, url={request.url}, data={data}")

        # 질문 생성 로직 구현
        quiz_response = get_first_question(body.memberId, body.topic, body.difficulty)

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

@router.post("/api/next-question/", response_model=NextQuestionResponse)
async def handle_next_question(request: Request, body: NextQuestionRequest):
    # 요청 시작 시각 기록
    start_time = time.time()
    try:
        # 요청 바디 데이터 기록
        data = await request.json()
        logger.info(f"Request received: method={request.method}, url={request.url}, data={data}")

        messageText = await transcribe_audio(body.filename)

        # 다음 질문 처리 로직 구현
        next_question_response = get_next_question(
            body.memberId,
            body.chatRoomId,
            body.messageId,
            messageText,
            body.topic,
            body.difficulty
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
            audioUrl=audio_url,
            messageText=messageText  
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

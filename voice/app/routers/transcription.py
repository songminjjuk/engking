from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.modules.transcribe import transcribe_audio
from app.modules.bedrock import send_to_bedrock
from app.modules.polly import synthesize_speech

router = APIRouter()

class TranscribeRequest(BaseModel):
    memberId: str
    chatRoomId: str
    messageId: str
    filename: str

class TranscriptResponse(BaseModel):
    success: bool
    memberId: str
    responseText: str
    audioUrl: str

@router.post("/api/transcription/", response_model=TranscriptResponse)
async def transcription_audio_file(request: TranscribeRequest):

    transcript = await transcribe_audio(request.audioUrl)

    # todo: b3_url 요청 후 응답

    bedrock_response = await send_to_bedrock(transcript)

    result_text = bedrock_response['result']
    memberId = bedrock_response['memberId']
    
    new_audio_filename = bedrock_response['new_filename']

    audio_url = synthesize_speech(result_text, new_audio_filename)

    # done: 회원번호 response 추가
    return TranscriptResponse(
        success=True,
        memberId=memberId,
        responseText=result_text,
        audioUrl=audio_url
    )

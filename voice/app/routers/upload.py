from fastapi import APIRouter, UploadFile, File, HTTPException
from app.modules.s3 import save_audio_to_s3
import os

router = APIRouter()

# 환경 변수에서 S3 버킷 이름 로드
BUCKET_NAME = os.getenv('BUCKET_NAME')

@router.post("/api/upload/")
async def upload_audio(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="파일이 필요합니다.")
    
    file_name = file.filename

    # 파일 내용을 읽음
    file_content = await file.read()
    
    # S3에 오디오 저장
    presigned_url = save_audio_to_s3(file_name, file_content)

    if not presigned_url:
        raise HTTPException(status_code=500, detail="S3에 오디오 저장 실패.")
    
    return {
        "file_name": file_name,
        "presignedUrl": presigned_url
        }

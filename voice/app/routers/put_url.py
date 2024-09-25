# app/routers/put_url.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,field_validator
from app.modules.s3 import generate_presigned_url

router = APIRouter()

# 요청 본문을 정의하는 Pydantic 모델
class FilenameRequest(BaseModel):
    filename: str

    @field_validator('filename')
    def check_not_empty(cls, value):
        if not value:
            raise ValueError('이 필드는 비어 있을 수 없습니다.')
        return value

@router.post("/api/create-put-url/")
async def create_put_url(request: FilenameRequest):
    if not request.filename:
        raise HTTPException(status_code=400, detail="파일명이 필요합니다.")
    
    presigned_url = generate_presigned_url(request.filename, 'put_object')

    if not presigned_url:
        raise HTTPException(status_code=500, detail="url 생성 실패.")
    
    return {"success": True, "presignedUrl": presigned_url}

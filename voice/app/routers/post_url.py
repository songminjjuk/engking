from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.modules.s3 import generate_presigned_post

router = APIRouter()

# 요청 본문을 정의하는 Pydantic 모델
class FilenameRequest(BaseModel):
    filename: str

@router.post("/api/create-post-url/")
async def create_post_url(request: FilenameRequest):
    if not request.filename:
        raise HTTPException(status_code=400, detail="파일명이 필요합니다.")

    presigned_post = generate_presigned_post(request.filename)

    if not presigned_post:
        raise HTTPException(status_code=500, detail="url 생성 실패.")
    
    return {"success": True, "presignedPost": presigned_post}

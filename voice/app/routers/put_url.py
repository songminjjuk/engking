# app/routers/put_url.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel,field_validator
from app.modules.s3 import generate_presigned_url
import time
from loguru import logger

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
async def create_put_url(request: Request,body: FilenameRequest):
    # 요청 시작 시각 기록
    start_time = time.time()

    try:
        # 요청 바디 데이터 기록
        data = await request.json()
        logger.info(f"Request received: method={request.method}, url={request.url}, data={data}")

        if not body.filename:
            raise HTTPException(status_code=400, detail="파일명이 필요합니다.")

        presigned_url = generate_presigned_url(body.filename, 'put_object')

        if not presigned_url:
            raise HTTPException(status_code=500, detail="url 생성 실패.")
        
        # 요청 처리 시간 기록
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # 밀리초로 변환

        # 응답 성공 로그 기록
        logger.info(f"Response successful: status=200, duration={duration:.2f}ms")

        return {"success": True, "presignedUrl": presigned_url}
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

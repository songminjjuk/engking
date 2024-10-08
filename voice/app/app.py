# app/app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import importlib
import logging
import re
import time
from fastapi.responses import JSONResponse
from loguru import logger

# .env 파일에서 환경 변수 로드
load_dotenv()

# 특수 문자 확인 함수
def contains_special_characters(s: str) -> bool:
    return bool(re.search(r'[^a-zA-Z0-9]', s))

aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

if contains_special_characters(aws_secret_access_key):
    print("AWS_SECRET_ACCESS_KEY에 특수 문자가 포함되어 있습니다.")
else:
    print("AWS_SECRET_ACCESS_KEY에 특수 문자가 포함되어 있지 않습니다.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://engking.site","*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uvicorn 기본 로거 가져오기
uvicorn_logger = logging.getLogger("uvicorn.access")

# /status 경로에 대한 로그를 필터링할 커스텀 필터 정의
class StatusLogFilter(logging.Filter):
    def filter(self, record):
        return "/status" not in record.getMessage()

# Uvicorn 로거에 필터 추가
uvicorn_logger.addFilter(StatusLogFilter())

# 라우터 자동 등록
routers_dir = 'app/routers'
for filename in os.listdir(routers_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = f'app.routers.{filename[:-3]}'  # .py 제거
        module = importlib.import_module(module_name)
        app.include_router(module.router)

# 헬스체크 엔드포인트 추가
@app.get("/status")
async def health_check():
    return {"status": "ok"}

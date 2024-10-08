# app/app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import importlib
from fastapi.responses import JSONResponse
import re  # 정규 표현식 모듈 추가
import time
from loguru import logger

# .env 파일에서 환경 변수 로드
load_dotenv()

# 특수 문자 확인 함수
def contains_special_characters(s: str) -> bool:
    # 정규 표현식으로 특수 문자 확인
    return bool(re.search(r'[^a-zA-Z0-9]', s))

aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# AWS 비밀 키에 특수 문자가 있는지 확인
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

# 전역 예외 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, e: HTTPException):
    # 요청 시작 시각 기록
    start_time = time.time()

    # 요청 처리 시간 기록
    end_time = time.time()
    duration = (end_time - start_time) * 1000  # 밀리초로 변환
    logger.error(f"HTTPException occurred: {str(e.detail)}, duration={duration:.2f}ms")

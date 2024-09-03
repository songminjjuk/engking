# app/app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import importlib
from fastapi.responses import JSONResponse

# .env 파일에서 환경 변수 로드
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# 전역 예외 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )

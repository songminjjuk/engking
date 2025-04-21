from fastapi import FastAPI
from routes import chat_routes, quiz_routes, evaluate_routes
import uvicorn
from config import settings
import time
from loguru import logger
import logging

app = FastAPI()

# 라우트 등록
app.include_router(chat_routes.router)
app.include_router(quiz_routes.router)
app.include_router(evaluate_routes.router)

# /status 요청을 필터링할 로거 필터 추가 (loguru 아님: uvicorn.access 용)
uvicorn_logger = logging.getLogger("uvicorn.access")

class StatusLogFilter(logging.Filter):
    def filter(self, record):
        return "/status" not in record.getMessage()

uvicorn_logger.addFilter(StatusLogFilter())

# 헬스 체크 라우트
@app.get("/healthz")
async def health_check1():
    return {"status": "ok"}

@app.get("/")
async def health_check2():
    return {"status": "ok"}

@app.get("/status")
async def health_check3():
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

from fastapi import FastAPI
from routes import chat_routes, quiz_routes, evaluate_routes
import uvicorn
from config import settings
import time
from loguru import logger
import logging  

app = FastAPI()

#### cicd check
# 라우트 등록
app.include_router(chat_routes.router)
app.include_router(quiz_routes.router)
app.include_router(evaluate_routes.router)

# Uvicorn의 access 로거 가져오기
uvicorn_logger = logging.getLogger("uvicorn.access")

# /status 경로에 대한 로그를 필터링할 커스텀 필터 정의
class StatusLogFilter(logging.Filter):
    def filter(self, record):
        return "/status" not in record.getMessage()

# Uvicorn 로거에 필터 추가
uvicorn_logger.addFilter(StatusLogFilter())

@app.get("/status")
async def health_check():
    
    return {"status": "ok"}
    # start_time = time.time()
    
    # # 요청 로깅
    # logger.info("Request received: method=GET, url=/status")

    # # 헬스 체크 처리
    # response_content = {"status": "ok"}

    # # 요청 처리 시간 계산
    # end_time = time.time()
    # duration = (end_time - start_time) * 1000  # 밀리초로 변환

    # # 응답 성공 로그 기록
    # logger.info(f"Response successful: status=200, duration={duration:.2f}ms")

if __name__ == '__main__':
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
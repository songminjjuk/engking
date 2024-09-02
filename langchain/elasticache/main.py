# app/main.py
from fastapi import FastAPI
from routes import chat_routes, quiz_routes, evaluation_routes, save_routes
import uvicorn

app = FastAPI()

# 라우트 등록
app.include_router(chat_routes.router, prefix="/chat")
app.include_router(quiz_routes.router, prefix="/quiz")
app.include_router(evaluation_routes.router, prefix="/chat/evaluate")
app.include_router(save_routes.router, prefix="/save")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)

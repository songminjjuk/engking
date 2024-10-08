from fastapi import FastAPI
from routes import chat_routes, quiz_routes, evaluate_routes
import uvicorn
from config import settings

app = FastAPI()

#### cicd check
# 라우트 등록
app.include_router(chat_routes.router)
app.include_router(quiz_routes.router)
app.include_router(evaluate_routes.router)

@app.get("/status")
async def health_check():
    return {"status": "ok"}
if __name__ == '__main__':
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

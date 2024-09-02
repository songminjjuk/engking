# app/main.py
from fastapi import FastAPI, Request
from api_handler import APIHandler
# from routes import chat_routes, quiz_routes, evaluation_routes, save_routes
import uvicorn

app = FastAPI()
api_handler = APIHandler()

@app.post("/stream/chat")
async def stream_chat_endpoint(request: Request):
    return await api_handler.stream_chat_endpoint(request)

@app.post("/stream/quiz")
async def stream_quiz_endpoint(request: Request):
    return await api_handler.stream_quiz_endpoint(request)

@app.post("/chat")
async def chat_endpoint(request: Request):
    return await api_handler.chat_endpoint(request)

@app.post("/quiz")
async def quiz_endpoint(request: Request):
    return await api_handler.quiz_endpoint(request)

@app.post("/chat/evaluate")
async def chat_evaluate_endpoint(request: Request):
    return await api_handler.chat_evaluate_endpoint(request)

@app.post("/quiz/evaluate")
async def quiz_evaluate_endpoint(request: Request):
    return await api_handler.quiz_evaluate_endpoint(request)

@app.post("/save")
async def save_endpoint(request: Request):
    return await api_handler.save_endpoint(request)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)


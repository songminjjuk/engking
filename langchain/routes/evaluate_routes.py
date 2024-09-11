from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
from services.evaluate_service import EvaluateService

router = APIRouter()

@router.post("/chat/evaluate")
async def chat_evaluate_endpoint(request: Request):
    data = await request.json()
    response_content = EvaluateService.evaluate_chat(data)
    # return JSONResponse(content=response_content)
    return response_content
@router.post("/quiz/evaluate")
async def quiz_evaluate_endpoint(request: Request):
    data = await request.json()
    response_content = EvaluateService.evaluate_quiz(data)
    # return JSONResponse(content=response_content)
    return response_content
from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
from services.quiz_service import QuizService

router = APIRouter()

@router.post("/quiz")
async def quiz_endpoint(request: Request):
    data = await request.json()
    response_content = QuizService.process_quiz(data)
    # return JSONResponse(content=response_content)
    return response_content

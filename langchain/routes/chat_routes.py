from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
from services.chat_service import ChatService

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    response_content = ChatService.process_chat(data)
    # return JSONResponse(content=response_content)
    return response_content

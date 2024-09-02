# app/routes/save_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.s3_service import S3Service
from app.services.memory_service import MemoryService

router = APIRouter()

# 필요한 서비스 초기화
s3_service = S3Service(bucket_name="your-bucket-name", region_name="your-region")
memory_service = MemoryService(redis_url="your-redis-url")

@router.post("/save")
async def save_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')

    memory = memory_service.get_memory(user_id, conversation_id)
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )

    s3_key = s3_service.save_conversation(user_name, conversation_id, conversation_text)

    return JSONResponse(content={"message": "Conversation saved", "s3_key": s3_key})

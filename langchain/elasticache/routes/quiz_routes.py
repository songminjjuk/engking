# app/routes/quiz_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.bedrock_service import BedrockService
from app.services.memory_service import MemoryService
from app.services.prompt_service import PromptService

router = APIRouter()

# 필요한 서비스 초기화
bedrock_service = BedrockService(model_id="your-model-id", region_name="your-region", role="your-role")
memory_service = MemoryService(redis_url="your-redis-url")
prompt_service = PromptService()

@router.post("/quiz")
async def quiz_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')

    memory = memory_service.get_memory(user_id, conversation_id)
    prompt_template = prompt_service.create_quiz_prompt_template(quiz_type, difficulty, first=True)
    conversation = ConversationChain(llm=bedrock_service.get_llm(), memory=memory, prompt=prompt_template, verbose=True)
    response_content = conversation.predict(input=user_input)

    return JSONResponse(content={
        "content": response_content,
        "user_id": user_id,
        "conversation_id": conversation_id
    })

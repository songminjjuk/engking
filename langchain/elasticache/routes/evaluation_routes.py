# app/routes/evaluation_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.bedrock_service import BedrockService
from app.services.memory_service import MemoryService

router = APIRouter()

# 필요한 서비스 초기화
bedrock_service = BedrockService(model_id="your-model-id", region_name="your-region", role="your-role")
memory_service = MemoryService(redis_url="your-redis-url")

@router.post("/chat/evaluate")
async def chat_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')

    memory = memory_service.get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No conversation history found"}, status_code=400)

    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )

    chat_evaluation_prompt = f"""
    Here is the conversation:\n{conversation_text}\n
    Please rate the user's language skills on a scale of 1 to 100 and provide feedback on how they can improve.
    Respond in the following JSON format:
    {{
        "score": "<numeric_score>",
        "feedback": "<feedback>"
    }}
    """
    response = bedrock_service.get_llm().invoke(chat_evaluation_prompt)
    memory_service.delete_memory(user_id, conversation_id)
    response_content = json.loads(response.content)
    return JSONResponse(content={
        "user_id": user_id,
        "conversation_id": conversation_id,
        "score": response_content.get("score"),
        "feedback": response_content.get("feedback")
    })

@router.post("/quiz/evaluate")
async def quiz_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    # user_name = data.get('user_name')

    memory = get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No quiz history found"}, status_code=400)

    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )
    print("conversation_text: ", conversation_text)
    quiz_evaluation_prompt=f"""
    Here is the quiz session:\n{conversation_text}\n
    Please fill in the "correct_answers" field with the number of correct answers the user provided, and the "total_questions" field with the total number of questions in the quiz. Additionally, provide feedback in the "feedback" field based on the user's performance.
    Respond in the following JSON format:
    {{
        "correct_answers": "<number_of_correct_answers>",
        "total_questions": "<total_number_of_questions>",
        "feedback": "<your_feedback>"
    }}
    """
    response = bedrock_llm.invoke(quiz_evaluation_prompt)
    delete_memory(user_id, conversation_id)
    response_content = json.loads(response.content)
    total_questions = int(response_content.get("total_questions"))
    correct_answers = int(response_content.get("correct_answers"))
    score = (correct_answers / total_questions) * 100
    score = round(score, 1)
    return JSONResponse(content={
        "user_id": user_id,
        "conversation_id": conversation_id,
        "score": str(score),
        "feedback": response_content.get("feedback")
    })
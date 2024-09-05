from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langchain.schema import HumanMessage, AIMessage
from langchain.chains import ConversationChain
from memory_manager import memory_manager
from prompt_manager import prompt_manager
from bedrock_client import bedrock_llm
from config import settings
import uvicorn, json

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', 'coffee')
    first = data.get('first', False)

    memory = memory_manager.get_memory(user_id, conversation_id)
    prompt_template = prompt_manager.create_chat_prompt_template(scenario, difficulty, first)
    conversation = ConversationChain(llm=bedrock_llm, memory=memory, prompt=prompt_template, verbose=True)
    response_content = conversation.predict(input=user_input)

    memory_manager.delete_memory(user_id, conversation_id)
    return JSONResponse(content={
        "content": response_content,
        "user_id": user_id,
        "conversation_id": conversation_id
    })

@app.post("/quiz")
async def quiz_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')
    first = data.get('first', False)

    memory = memory_manager.get_memory(user_id, conversation_id)
    prompt_template = prompt_manager.create_quiz_prompt_template(quiz_type, difficulty, first)
    conversation = ConversationChain(llm=bedrock_llm, memory=memory, prompt=prompt_template, verbose=True)
    response_content = conversation.predict(input=user_input)

    memory_manager.delete_memory(user_id, conversation_id)
    return JSONResponse(content={
        "content": response_content,
        "user_id": user_id,
        "conversation_id": conversation_id
    })
# 대화 평가 API 엔드포인트
@app.post("/chat/evaluate")
async def chat_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    memory = memory_manager.get_memory(user_id, conversation_id)
    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No conversation history found"}, status_code=400)
    messages = memory.chat_memory.messages

    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in messages
    )


    print("conversation_text: ", conversation_text)
    chat_evaluation_prompt = f"""
    You are an expert in evaluating language skills based on conversations. Below is a conversation between a user and an AI.
    Please evaluate the user's language skills on a scale of 1 to 100 and provide detailed feedback on how they can improve in Korean.
    Ensure your response is strictly in the following JSON format without any additional comments or text:

    {{
        "score": "<percentage_score as string>",
        "feedback": "<feedback in Korean>"
    }}

    The response should be a valid JSON string only.
    Conversation:
    {conversation_text}
    Remember, your response should be a valid JSON string, and do not include any extra information or comments outside the JSON.
    """

    response = bedrock_llm.invoke(chat_evaluation_prompt)
    memory_manager.delete_memory(user_id, conversation_id)
    try:
        response_content = json.loads(response.content)
        feedback = response_content.get("feedback")
        score = response_content.get("score")

        return JSONResponse(content={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "score": str(score),
            "feedback": feedback
        })
    except json.JSONDecodeError as e:
    # JSON 디코딩 오류 처리
        print(f"JSONDecodeError: {str(e)} - Response content: {response.content}")
        return JSONResponse(content={"error": "Invalid response from the LLM service"}, status_code=500)

    except ValueError as e:
    # ValueError 처리 (예: total_questions가 0일 때)
        print(f"ValueError: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

    except Exception as e:
    # 그 외의 일반적인 오류 처리
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(content={"error": "An unexpected error occurred."}, status_code=500)
    

# 퀴즈 평가 API 엔드포인트
@app.post("/quiz/evaluate")
async def quiz_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')

    memory = memory_manager.get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No quiz history found"}, status_code=400)
    messages = memory.chat_memory.messages

    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in messages
    )

    print("conversation_text: ", conversation_text)
    quiz_evaluation_prompt = f"""
    You are an expert at evaluating quiz sessions. Below is a conversation that includes a quiz session.
    Please evaluate the session by calculating the score as a percentage based on the number of correct answers and total questions. 
    Additionally, provide detailed feedback in Korean on the user's performance. 
    Make sure to return the response strictly in a valid JSON format.

    Conversation:
    {conversation_text}

    Please respond in the following JSON format:
    {{
        "score": "<percentage_score as string>",
        "feedback": "<feedback in Korean>"
    }}

    Remember, your response should be a valid JSON string, and do not include any extra information or comments outside the JSON.
    """
    response = bedrock_llm.invoke(quiz_evaluation_prompt)
    memory_manager.delete_memory(user_id, conversation_id)
    try:
        response_content = json.loads(response.content)
        feedback = response_content.get("feedback")
        score = response_content.get("score")
        return JSONResponse(content={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "score": str(score),
            "feedback": feedback
        })
    except json.JSONDecodeError as e:
    # JSON 디코딩 오류 처리
        print(f"JSONDecodeError: {str(e)} - Response content: {response.content}")
        return JSONResponse(content={"error": "Invalid response from the LLM service"}, status_code=500)

    except ValueError as e:
    # ValueError 처리 (예: total_questions가 0일 때)
        print(f"ValueError: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

    except Exception as e:
    # 그 외의 일반적인 오류 처리
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(content={"error": "An unexpected error occurred."}, status_code=500)
if __name__ == '__main__':
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

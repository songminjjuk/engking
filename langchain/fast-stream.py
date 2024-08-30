import boto3
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime
import uvicorn
import json

app = FastAPI()

s3_client = boto3.client('s3', region_name='ap-northeast-1')

# S3 버킷 이름
S3_BUCKET_NAME = 'mmmybucckeet'
quiz_example_output = """
    Example format:
    <Question Number> <Question>
    A) <Option 1>
    B) <Option 2>
    C) <Option 3>
    D) <Option 4>
    """
# 전역 메모리 저장소
memory_store = {}

def initialize_bedrock_client(model_id, region_name):
    return ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0),
        region_name=region_name,
        streaming=True,
        client=boto3.client("bedrock-runtime", region_name=region_name)
    )

bedrock_llm = initialize_bedrock_client(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="ap-northeast-1"
)

def get_memory(user_id, conversation_id):
    # 이 부분이 back api를 호출해서 DynampDB에서
    #  user_id, conversation_id를 기반으로 조회해서 
    # 값을 가져오는 걸로 바뀔 듯
    memory_key = f"{user_id}_{conversation_id}"
    
    if memory_key not in memory_store:
        memory_store[memory_key] = ConversationBufferMemory(return_messages=True, memory_key="history", input_key="human", output_key="ai")
    return memory_store[memory_key]

def delete_memory(user_id, conversation_id):
    memory_key = f"{user_id}_{conversation_id}"
    if memory_key in memory_store:
        del memory_store[memory_key]

def create_chat_prompt_template(difficulty, scenario, history):
    scenario_prompts = {
        "hamburger": "You are an expert in helping customers order hamburgers. Guide the user through ordering a hamburger, including selecting ingredients, sides, and drinks.",
        "travel": "You are an immigration officer assisting a traveler. Help the user go through the immigration process, including answering questions about their trip and providing necessary documentation.",
        "coffee": "You are an expert barista helping a customer order coffee. Guide the user through choosing their coffee type, size, and any additional preferences like milk, sugar, or flavorings.",
        "meeting": "You are a professional meeting coordinator. Help the user organize a meeting, including setting the agenda, scheduling, and inviting participants.",
        "movie": "You are a cinema ticket booking assistant. Help the user book a movie ticket, including selecting the movie, showtime, and seating preferences.",
        "music": "You are a music enthusiast engaging in a conversation about music. Discuss various genres, artists, or specific songs based on the user's interests."
    }

    difficulty_prompts = {
        "Easy": "Additionally, the difficulty level is Easy, Use simple and direct language. Keep your responses short and avoid complex details.",
        "Normal": "Additionally, the difficulty level is Normal, Use moderate language with some detail. Provide clear explanations but avoid overly complex terms.",
        "Hard": "Additionally, the difficulty level is Hard, Use complex and detailed language. Include nuanced explanations and advanced vocabulary in your responses."
    }

    scenario_prompt = scenario_prompts.get(scenario)
    difficulty_prompt = difficulty_prompts.get(difficulty)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", f"{scenario_prompt} {difficulty_prompt}. Please ask the user a question directly without any introductory phrases.\nchat_history: {history}"),
            ("human", "{{input}}")
        ]
    )
    return prompt_template
def create_quiz_prompt_template(quiz_type, difficulty, history):
    quiz_type_prompts = {
        "vocabulary": "You are an expert at creating vocabulary quizzes. Create a quiz where the user needs to identify the correct word based on the context.",
        "grammar": "You are an expert at creating grammar quizzes. Create a quiz where the user needs to identify the correct grammar usage."
    }   

    difficulty_prompts = {
        "Easy": "Additionally, the difficulty level is Easy, so create the quiz with simple and direct expressions.",
        "Normal": "Additionally, the difficulty level is Normal, so create the quiz with moderate expressions that include some details.",
        "Hard": "Additionally, the difficulty level is Hard, so create the quiz with complex and detailed expressions."
    }

    # 퀴즈 출력 예시를 프롬프트에 포함

    quiz_prompt = quiz_type_prompts.get(quiz_type)
    difficulty_prompt = difficulty_prompts.get(difficulty)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", f"{quiz_prompt} {difficulty_prompt} Generate only one quiz question. Use the following format: {quiz_example_output}. Ask a question right away without any introductory text, and do not generate multiple questions.\nchat_history: {history}"),
            ("human", "{{input}}")
        ]
    )

    return prompt_template

async def stream_chat_get_response_from_claude(user_id, conversation_id, difficulty, scenario, user_input):
    memory = get_memory(user_id, conversation_id)
    
    # 대화 히스토리를 가져옴
    history = memory.load_memory_variables({}).get("history", "")
    prompt_template = create_chat_prompt_template(difficulty, scenario, history)
    prompt_text = prompt_template.format(input=user_input)
    
    async def stream_response():
        full_response = ""
        async for chunk in bedrock_llm.astream(prompt_text):
            response_content = chunk.content
            print(response_content, end="", flush=True)
            yield response_content
            full_response += response_content  # 응답을 누적
            
        # 새로운 대화 내용을 메모리에 저장
        memory.save_context({"human": user_input}, {"ai": full_response})
        print(memory.load_memory_variables({}))
    return StreamingResponse(stream_response(), media_type="text/plain")

async def stream_quiz_get_response_from_claude(user_id, conversation_id, quiz_type, difficulty, user_input):
    memory = get_memory(user_id, conversation_id)

    # 대화 히스토리를 가져옴
    history = memory.load_memory_variables({}).get("history", "")
    prompt_template = create_quiz_prompt_template(quiz_type, difficulty, history)
    prompt_text = prompt_template.format(input=user_input)
    
    async def stream_response():
        full_response = ""
        async for chunk in bedrock_llm.astream(prompt_text):
            response_content = chunk.content
            print(response_content, end="", flush=True)
            yield response_content
            full_response += response_content  # 응답을 누적
    
        # 새로운 대화 내용을 메모리에 저장
        memory.save_context({"human": user_input}, {"ai": full_response})
        print(memory.load_memory_variables({}))
    return StreamingResponse(stream_response(), media_type="text/plain")
async def chat_get_response_from_claude(user_id, conversation_id, difficulty, scenario, user_input):
    memory = get_memory(user_id, conversation_id)
    
    # 대화 히스토리를 가져옴
    history = memory.load_memory_variables({}).get("history", "")
    prompt_template = create_chat_prompt_template(difficulty, scenario, history)
    prompt_text = prompt_template.format(input=user_input)
    print("prompt_text: ", prompt_text)
    response = bedrock_llm.invoke(prompt_text)
    response_content = response.content # 응답만 추출
    # 새로운 대화 내용을 메모리에 저장
    memory.save_context({"human": user_input}, {"ai": response_content})
    print(memory.load_memory_variables({}))
    return JSONResponse(content={
        "content": response_content,
        "user_id": user_id,
        "conversation_id": conversation_id
    })

async def quiz_get_response_from_claude(user_id, conversation_id, quiz_type, difficulty, user_input):
    memory = get_memory(user_id, conversation_id)

    # 대화 히스토리를 가져옴
    history = memory.load_memory_variables({}).get("history", "")
    prompt_template = create_quiz_prompt_template(quiz_type, difficulty, history)
    prompt_text = prompt_template.format(input=user_input)
    print("prompt_text: ", prompt_text)
    response = bedrock_llm.invoke(prompt_text)
    response_content = response.content
    # 새로운 대화 내용을 메모리에 저장
    memory.save_context({"human": user_input}, {"ai": response_content})
    print(memory.load_memory_variables({}))
    return JSONResponse(content={
        "content": response_content,
        "user_id": user_id,
        "conversation_id": conversation_id
    })

async def save_conversation_to_s3(user_id, conversation_id, user_name):
    memory = get_memory(user_id, conversation_id)
    s3_client = boto3.client('s3')

    # 대화 내용을 텍스트 형식으로 변환
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )
    
    # 파일 이름 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"{user_name}/conversation_{conversation_id}_{timestamp}.txt"

    # S3에 파일 업로드
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        Body=conversation_text.encode('utf-8')
    )

    return s3_key

@app.post("/stream/chat")
async def stream_chat_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', 'coffee')

    return await stream_chat_get_response_from_claude(user_id, conversation_id, difficulty, scenario, user_input)

@app.post("/stream/quiz")
async def stream_quiz_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')

    return await stream_quiz_get_response_from_claude(user_id, conversation_id, quiz_type, difficulty, user_input)

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', 'coffee')

    return await chat_get_response_from_claude(user_id, conversation_id, difficulty, scenario, user_input)

@app.post("/quiz")
async def quiz_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')

    return await quiz_get_response_from_claude(user_id, conversation_id, quiz_type, difficulty, user_input)

@app.post("/chat/evaluate")
async def chat_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')
    memory = get_memory(user_id, conversation_id)

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
    response = bedrock_llm.invoke(chat_evaluation_prompt)
    delete_memory(user_id, conversation_id)
    response_content=json.loads(response.content)
    print(response_content)
    return JSONResponse(content={
        "user_id": user_id,
        "conversation_id": conversation_id,
        "score": response_content.get("score"),
        "feedback": response_content.get("feedback")
    })

@app.post("/quiz/evaluate")
async def quiz_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')
    memory = get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No quiz history found"}, status_code=400)
    
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )
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
    print("response: ", response)
    response_content = json.loads(response.content)
    print("response_content: ", response_content)
    total_questions = int(response_content.get("total_questions"))
    correct_answers = int(response_content.get("correct_answers"))
    score = (total_questions/correct_answers) * 100
    score = round(score, 1) # 반올림
    score = str(score)
    return JSONResponse(content={
        "user_id": user_id,
        "conversation_id": conversation_id,
        "score": score,
        "feedback": response_content.get("feedback")
    })
    
@app.post("/save")
async def save_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')

    if not user_id or not conversation_id:
        return JSONResponse(content={"error": "User ID and conversation ID are required"}, status_code=400)

    s3_key = await save_conversation_to_s3(user_id, conversation_id, user_name)
    
    return JSONResponse(content={"message": "Conversation saved", "s3_key": s3_key})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
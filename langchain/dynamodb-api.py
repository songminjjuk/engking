import os
import boto3
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_aws import ChatBedrock
from langchain.memory import ConversationBufferMemory, RedisChatMessageHistory
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate
from datetime import datetime
import uvicorn
from langchain.schema import HumanMessage, AIMessage
import requests

app = FastAPI()

# 기존의 메모리 저장소
memory_store = {}

quiz_example_output = """
    Example format:
    <Question Number> <Question>
    A) <Option 1>
    B) <Option 2>
    C) <Option 3>
    D) <Option 4>
    """

# S3 버킷 설정
S3_BUCKET_NAME = 'mmmybucckeet'
s3_client = boto3.client('s3', region_name='ap-northeast-1')

# Redis URL, DB URL 가져오기
db_url = ""

# Bedrock 클라이언트 초기화
def initialize_bedrock_client(model_id, region_name):
    return ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0.5),
        region_name=region_name,
        streaming=True,
        client=boto3.client("bedrock-runtime", region_name=region_name)
    )

bedrock_llm = initialize_bedrock_client(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="ap-northeast-1"
)

# 메모리 관리 함수
def get_memory(user_id, conversation_id):
    # print("Connecting to Redis:", redis_url)
    # # 혹은 단순한 연결 테스트
    # try:
    #     r = redis.StrictRedis.from_url(redis_url)
    #     r.ping()
    #     print("Redis connection successful")
    # except Exception as e:
    #     print("Failed to connect to Redis:", str(e))

    # memory_key = f"{user_id}_{conversation_id}"
    # print("memory_key: ", memory_key)
    # print("Creating RedisChatMessageHistory...")
    # chat_history = RedisChatMessageHistory(session_id=memory_key, url=redis_url, key_prefix="chat_history:")
    # print("RedisChatMessageHistory created successfully")
    # print("Creating ConversationBufferMemory...")
    # memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True, memory_key="history")
    # print("ConversationBufferMemory created successfully")
    # print("memory: ", memory)
    # return memory
    api_endpoint = f"{db_url}/chatmessage/allmessages"
    request_data = {
        "memberId": user_id,            
        "chatRoomId": conversation_id  
    }
    # API 요청 보내기
    response = requests.post(api_endpoint, json=request_data)

    if response.status_code == 200:
        # 성공적으로 데이터를 받아온 경우
        response_data = response.json()
        # print("response_data: ", response_data)
        memory_key = f"{user_id}_{conversation_id}"
        # 메모리 객체가 없으면 생성
        if memory_key not in memory_store:
            memory_store[memory_key] = ConversationBufferMemory(return_messages=True, memory_key="history")
        #, input_key="human", output_key="ai")
        memory = memory_store[memory_key]


        # 응답 데이터를 memory에 저장
        for message in response_data:
            sender_id = message.get("senderId")
            message_text = message.get("messageText", "")

            # if sender_id == "AI":
            #     memory.save_context({}, {"output": message_text})
            # else:
            #     memory.save_context({"input": message_text}, {})
            if sender_id == "AI" and message_text:
                # AI가 보낸 메시지로 AIMessage로 저장
                memory.chat_memory.add_ai_message(AIMessage(content=message_text))
            elif message_text:  # 사용자 메시지를 HumanMessage로 저장
                memory.chat_memory.add_user_message(HumanMessage(content=message_text))
        print("get_memory: ", memory)
        return memory
    else:
        # 요청이 실패한 경우 에러 처리
        print(f"Failed to retrieve messages. Status code: {response.status_code}")
        print("Error:", response.text)
        return None

# 메모리 삭제 함수
# def delete_memory(user_id, conversation_id):
#     memory_key = f"{user_id}_{conversation_id}"
#     chat_history = RedisChatMessageHistory(session_id=memory_key, url=redis_url, key_prefix="chat_history:")
#     chat_history.clear()

def delete_memory(user_id, conversation_id):
    memory_key = f"{user_id}_{conversation_id}"
    if memory_key in memory_store:
        del memory_store[memory_key]

# Chat Prompt 템플릿 생성 함수
def create_chat_prompt_template(scenario, difficulty, first):
    scenario_prompts = {
            "hamburger": (
                "You are an expert in helping customers order hamburgers. Guide the user through ordering a hamburger. "
                "Start by asking if they want a hamburger, cheeseburger, or a special burger. "
                "Then, ask whether they want it as a single item or as part of a combo meal. "
                "If a combo meal, ask about their preferred side (fries, salad, etc.) and drink (soda, water, etc.). "
                "Next, inquire about the size of the burger (small, medium, large) and any additional toppings "
                "(lettuce, tomato, pickles, onions, cheese, etc.). "
                "Finally, ask if they prefer to eat in or take out."
            ),
            "travel": (
                "You are an immigration officer assisting a traveler. Help the user go through the immigration process. "
                "Begin by asking for their passport and travel documents. "
                "Then, inquire about the purpose of their visit (business, tourism, visiting family, etc.) and the duration of their stay. "
                "Ask about their accommodation details (hotel, Airbnb, staying with friends/family), and confirm their return or onward ticket. "
                "Finally, ensure they are aware of the local customs and regulations, and offer any necessary advice for their stay."
            ),
            "coffee": (
                "You are an expert barista helping a customer order coffee. Guide the user through choosing their coffee. "
                "Start by asking what type of coffee they would like (espresso, americano, latte, cappuccino, etc.). "
                "Next, ask about the size (small, medium, large) and whether they prefer it hot or iced. "
                "Inquire about their preference for milk options (regular, skim, soy, almond, etc.) and sweeteners (sugar, honey, syrup, etc.). "
                "Finally, ask if they want any additional flavors (vanilla, caramel, hazelnut) or toppings (whipped cream, chocolate sprinkles). "
                "Conclude by asking if they would like to enjoy their coffee in-store or take it to go."
            ),
            "meeting": (
                "You are a professional meeting coordinator. Help the user organize a meeting. "
                "Start by confirming the purpose of the meeting and the key topics to be discussed. "
                "Then, help the user schedule the meeting, ensuring the date and time are convenient for all participants. "
                "Assist in creating an agenda, including time allocations for each topic. "
                "Next, discuss the format of the meeting (in-person, video conference, hybrid) and suggest appropriate tools "
                "or platforms (Zoom, Microsoft Teams, Google Meet, etc.). "
                "Finally, guide the user in sending out invitations and setting up reminders for the participants."
            ),
            "movie": (
                "You are a cinema ticket booking assistant. Help the user book a movie ticket. "
                "Start by asking which movie they would like to see and confirm the preferred showtime. "
                "Inquire about the type of ticket they want (standard, 3D, IMAX) and the number of tickets needed. "
                "Next, ask about seating preferences (front row, middle, back, aisle seat) and check for availability. "
                "Then, offer any additional services such as snacks and drinks to be ordered in advance. "
                "Finally, confirm the booking details and ask if they want to receive the tickets digitally or pick them up at the theater."
            ),
            "music": (
                "You are a music enthusiast engaging in a conversation about music. Guide the user through a discussion about music. "
                "Start by asking about their favorite genres or artists. "
                "Inquire about their recent favorite songs or albums and discuss what they like about them. "
                "Then, ask if they play any musical instruments or have ever attended live concerts. "
                "Suggest similar artists or tracks based on their preferences and ask if they have any music recommendations. "
                "Finally, discuss the user's thoughts on recent trends in the music industry, such as streaming services, vinyl revival, or the impact of social media on music discovery."
            )
        }

    difficulty_prompts = {
        "Easy": "Additionally, the difficulty level is Easy, Use simple and direct language. Keep your responses short and avoid complex details.",
        "Normal": "Additionally, the difficulty level is Normal, Use moderate language with some detail. Provide clear explanations but avoid overly complex terms.",
        "Hard": "Additionally, the difficulty level is Hard, Use complex and detailed language. Include nuanced explanations and advanced vocabulary in your responses."
    }

    scenario_prompt = scenario_prompts.get(scenario, "You are a helpful assistant.")
    difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")
    if first:
        system_prompt = f"{scenario_prompt} {difficulty_prompt} Please ask the user a question directly without any introductory phrases.\nchat_history:{{history}}"
    else:
        system_prompt = f"Please remember the initial instructions and continue to generate responses accordingly. Ask the user a question directly without any introductory phrases.\nchat_history:{{history}}"
        

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )
    # print("prompt_template", prompt_template)
    return prompt_template

def create_quiz_prompt_template(quiz_type, difficulty, first):
    quiz_type_prompts = {
        "vocabulary": "You are an expert at creating vocabulary quizzes. Create a quiz where the user needs to identify the correct word based on the context.",
        "grammar": "You are an expert at creating grammar quizzes. Create a quiz where the user needs to identify the correct grammar usage."
    }

    difficulty_prompts = {
        "Easy": "Additionally, the difficulty level is Easy, so create the quiz with simple and clear expressions similar to those found in the easier sections of TOEIC exams. "
                "Use basic vocabulary and straightforward sentence structures, ensuring the question is accessible to beginners.",
        
        "Normal": "Additionally, the difficulty level is Normal, so create the quiz with clear and concise expressions similar to those found in TOEIC exams. "
                "Ensure that the language and structure are practical and commonly used in everyday situations, focusing on moderate difficulty.",

        "Hard": "Additionally, the difficulty level is Hard, so create the quiz with expressions similar to the more challenging sections of TOEIC exams. "
                "Use more complex sentence structures and a wider range of vocabulary, but still keep it relevant to TOEIC standards."
    }

    quiz_prompt = quiz_type_prompts.get(quiz_type, "You are a helpful assistant creating quizzes.")
    difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")

    # 첫 번째 요청일 때는 상세한 지침을 포함하여 프롬프트 생성
    if first:
        system_prompt = f"{quiz_prompt} {difficulty_prompt} Please generate only one quiz question. Use the following format: {quiz_example_output}. " \
                        "Do not provide explanations or feedback. Focus solely on generating the quiz question in the specified format without any introductory text. " \
                        f"\nchat_history:{{history}}"
    else:
        # 이후 요청일 때는 간단하게 지침을 상기시키는 메시지를 포함
        system_prompt = f"Please remember the initial instructions: generate only one quiz question in the specified format. " \
                        "Do not provide any feedback or explanations. Focus solely on generating the quiz question. " \
                        f"Remember that Use the following format: {quiz_example_output}" \
                        f"\nchat_history:{{history}}"

    # 프롬프트 템플릿 구성
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )

    return prompt_template


# 대화 API 엔드포인트
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', 'coffee')
    first = data.get('first', False)
    print("user_id: ", user_id)
    memory = get_memory(user_id, conversation_id) # db에서 갖고와서 history에 저장 즉, 대화 이력 가져오기
    # print("memory: ", memory.load_memory_variables({}).get("history", ""))
    prompt_template = create_chat_prompt_template(scenario, difficulty, first)
    conversation = ConversationChain(llm=bedrock_llm, memory=memory, prompt=prompt_template, verbose=True)
    print("conversation: ", conversation)
    response_content = conversation.predict(input=user_input)
    
    # # memory에 사용자 입력과 AI 응답 추가
    # print("zz memory start~")
    # memory.chat_memory.add_user_message(HumanMessage(content=user_input))
    # print("Added user message to memory.")
    # memory.chat_memory.add_ai_message(AIMessage(content=response_content))
    print("memory: ", memory.load_memory_variables({}).get("history", ""))
    # print("Added AI message to memory.")
    print("response: ", response_content)
    delete_memory(user_id, conversation_id)
    return JSONResponse(content={
        "content": response_content,
        "user_id": user_id,
        "conversation_id": conversation_id
    })

# 퀴즈 API 엔드포인트
@app.post("/quiz")
async def quiz_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')
    first = data.get('first', False)
    memory = get_memory(user_id, conversation_id) # db에서 갖고와서 history에 저장 즉, 대화 이력 가져오기
    print("memory: ", memory.load_memory_variables({}).get("history", ""))
    prompt_template = create_quiz_prompt_template(quiz_type, difficulty, first)
    conversation = ConversationChain(llm=bedrock_llm, memory=memory, prompt=prompt_template, verbose=True)
    print("conversation: ", conversation)
    response_content = conversation.predict(input=user_input)

    # # memory에 사용자 입력과 AI 응답 추가
    # print("zz memory start~")
    # memory.chat_memory.add_user_message(HumanMessage(content=user_input))
    # print("Added user message to memory.")
    # memory.chat_memory.add_ai_message(AIMessage(content=response_content))
    # print("Added AI message to memory.")
    # print(response_content)
    delete_memory(user_id, conversation_id)
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
    # user_name = data.get('user_name')
    memory = get_memory(user_id, conversation_id)
    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No conversation history found"}, status_code=400)
    messages = memory.chat_memory.messages
    # if messages and isinstance(messages[-1], AIMessage):
    #     messages = messages[:-1]  # 마지막 메시지 제거
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        #for message in memory.chat_memory.messages
        for message in messages
    )


    print("conversation_text: ", conversation_text)
    chat_evaluation_prompt = f"""
    You are an expert in evaluating language skills based on conversations. Below is a conversation between a user and an AI.
    Please evaluate the user's language skills on a scale of 1 to 100 and provide detailed feedback on how they can improve.
    Ensure your response is strictly in the following JSON format without any additional comments or text:

    {{
        "score": "<numeric_score>",
        "feedback": "<feedback>"
    }}

    The response should be a valid JSON string only.
    Conversation:
    {conversation_text}
    """

    response = bedrock_llm.invoke(chat_evaluation_prompt)

    # 응답이 유효한 JSON 형식인지 확인
    try:
        response_content = json.loads(response.content)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {str(e)} - Response content: {response.content}")
        return JSONResponse(content={"error": "Invalid response from the LLM service"}, status_code=500)

    delete_memory(user_id, conversation_id)

    return JSONResponse(content={
        "user_id": user_id,
        "conversation_id": conversation_id,
        "score": response_content.get("score"),
        "feedback": response_content.get("feedback")
    })

# 퀴즈 평가 API 엔드포인트
@app.post("/quiz/evaluate")
async def quiz_evaluate_endpoint(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    # user_name = data.get('user_name')

    memory = get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return JSONResponse(content={"error": "No quiz history found"}, status_code=400)
    messages = memory.chat_memory.messages

    # if messages and isinstance(messages[-1], AIMessage):
    #     messages = messages[:-1]
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        #for message in memory.chat_memory.messages
        for message in messages
    )

    print("conversation_text: ", conversation_text)
    quiz_evaluation_prompt = f"""
    You are an expert at evaluating quiz sessions. Below is a conversation that includes a quiz session.
    Please evaluate the session by filling in the number of correct answers, total questions, and provide feedback.
    Make sure to return the response strictly in a valid JSON format.

    Conversation:
    {conversation_text}

    Please respond in the following JSON format:
    {{
        "correct_answers": "<number_of_correct_answers>",
        "total_questions": "<total_number_of_questions>",
        "feedback": "<your_feedback>"
    }}

    Remember, your response should be a valid JSON string, and do not include any extra information or comments outside the JSON.
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

# 대화 저장 API 엔드포인트
# @app.post("/save")
# async def save_endpoint(request: Request):
#     data = await request.json()
#     user_id = data.get('user_id')
#     conversation_id = data.get('conversation_id')
#     user_name = data.get('user_name')

#     memory = get_memory(user_id, conversation_id)
#     s3_key = await save_conversation_to_s3(user_id, conversation_id, user_name, memory)

#     return JSONResponse(content={"message": "Conversation saved", "s3_key": s3_key})

# async def save_conversation_to_s3(user_id, conversation_id, user_name, memory):
#     # 대화 내용을 텍스트 형식으로 변환
#     conversation_text = "\n".join(
#         f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
#         for message in memory.chat_memory.messages
#     )

#     # 파일 이름 생성
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     s3_key = f"{user_name}/conversation_{conversation_id}_{timestamp}.txt"

#     # S3에 파일 업로드
#     s3_client.put_object(
#         Bucket=S3_BUCKET_NAME,
#         Key=s3_key,
#         Body=conversation_text.encode('utf-8')
#     )

#     return s3_key

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)

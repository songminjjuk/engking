import boto3
from flask import Flask, request, jsonify
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime

app = Flask(__name__)

s3_client = boto3.client('s3', region_name='ap-northeast-1')

# S3 버킷 이름
S3_BUCKET_NAME = 'mmmybucckeet'

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
    memory_key = f"{user_id}_{conversation_id}"
    if memory_key not in memory_store:
        memory_store[memory_key] = ConversationBufferMemory(return_messages=True)
    return memory_store[memory_key]

def create_chat_prompt_template(difficulty, scenario):
    scenario_prompts = {
        "햄버거 주문하기": "You are helping a customer order a hamburger.",
        "입국 심사하기": "You are assisting a traveler going through immigration.",
        "커피 주문하기": "You are helping a customer order a coffee."
    }

    difficulty_prompts = {
        "Easy": "Use simple and straightforward language.",
        "Normal": "Use moderate language with some detail.",
        "Hard": "Use complex and detailed language."
    }

    scenario_prompt = scenario_prompts.get(scenario, "You are a helpful assistant.")
    difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", f"{scenario_prompt} {difficulty_prompt}. Please ask the user a question directly without any introductory phrases.\n{{history}}"),
            ("human", "{input}")
        ]
    )
    return prompt_template

def create_quiz_prompt_template(quiz_type, difficulty):
    quiz_type_prompts = {
        "vocabulary": "You are a helpful assistant creating a vocabulary quiz. Ask questions where the user needs to select the correct word in context.",
        "grammar": "You are a helpful assistant creating a grammar quiz. Ask questions where the user needs to identify the correct grammar usage."
    }

    difficulty_prompts = {
        "Easy": "Use simple and straightforward language.",
        "Normal": "Use moderate language with some detail.",
        "Hard": "Use complex and detailed language."
    }

    quiz_prompt = quiz_type_prompts.get(quiz_type, "You are a helpful assistant creating a quiz.")
    difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", f"{quiz_prompt} {difficulty_prompt}. Generate the quiz based on the user's selected difficulty level. Ask the quiz question directly without any introductory phrases, do not respond to the user's answer, and move immediately to the next question.\n{{history}}"),
            ("human", "{input}")
        ]
    )

    return prompt_template

def chat_get_response_from_claude(user_id, conversation_id, difficulty, scenario, user_input):
    memory = get_memory(user_id, conversation_id)
    prompt_template = create_chat_prompt_template(difficulty, scenario)
    conversation = ConversationChain(
        llm=bedrock_llm,
        prompt=prompt_template,
        memory=memory
    )
    response = conversation.predict(input=user_input)
    print(response)
    return response

def quiz_get_response_from_claude(user_id, conversation_id, quiz_type, difficulty, user_input):
    memory = get_memory(user_id, conversation_id)
    prompt_template = create_quiz_prompt_template(quiz_type, difficulty)
    conversation = ConversationChain(
        llm=bedrock_llm,
        prompt=prompt_template,
        memory=memory
    )
    # response =""
    # for chunk in conversation.stream(user_input):
    #     response += chunk["response"]
    #     print(response, end="", flush=True)  # 실시간으로 출력
    response = conversation.predict(input=user_input)
    print(response)
    return response

def save_conversation_to_s3(user_id, conversation_id, user_name):
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

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', '커피 주문하기')

    return chat_get_response_from_claude(user_id, conversation_id, difficulty, scenario, user_input)

@app.route('/quiz', methods=['POST'])
def quiz_endpoint():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')

    return quiz_get_response_from_claude(user_id, conversation_id, quiz_type, difficulty, user_input)

@app.route('/chat/evaluate', methods=['POST'])
def chat_evaluate_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')
    memory = get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return jsonify({"error": "No conversation history found"}), 400
    
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
        "feedback": "<your_feedback>"
    }}
    """
    # Claude에게 점수 요청
    response = bedrock_llm.invoke(chat_evaluation_prompt)
    # print(response)
    return jsonify({"score": response.content})

@app.route('/quiz/evaluate', methods=['POST'])
def quiz_evaluate_endpoint():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    conversation_id = data.get('conversation_id')
    
    memory = get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return jsonify({"error": "No quiz history found"}), 400
    
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )
    
    # 전체 퀴즈에 대한 피드백 요청
    feedback_prompt = f"Here is the quiz session:\n{conversation_text}\nPlease provide feedback on which answers were correct or incorrect, and suggest areas for improvement."

    # Claude에게 피드백 요청
    response = bedrock_llm.invoke(feedback_prompt)
    # print(response)
    return jsonify({"feedback": response.content})

@app.route('/save', methods=['POST'])
def save_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')
    if not user_id or not conversation_id:
        return jsonify({"error": "User ID and conversation ID are required"}), 400

    # 대화 내용 S3에 저장
    s3_key = save_conversation_to_s3(user_id, conversation_id, user_name)

    return jsonify({"message": "Conversation saved", "s3_key": s3_key})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

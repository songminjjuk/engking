import boto3
from flask import Flask, request, jsonify
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime

app = Flask(__name__)

class BedrockClient:
    def __init__(self, model_id, region_name):
        self.client = ChatBedrock(
            model_id=model_id,
            model_kwargs=dict(temperature=0),
            region_name=region_name,
            client=boto3.client("bedrock-runtime", region_name=region_name)
        )

    def get_client(self):
        return self.client

bedrock_llm = BedrockClient(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="ap-northeast-1"
).get_client()

class MemoryManager:
    def __init__(self):
        self.memory_store = {}

    def get_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        if memory_key not in self.memory_store:
            self.memory_store[memory_key] = ConversationBufferMemory(return_messages=True)
        return self.memory_store[memory_key]

    def delete_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        if memory_key in self.memory_store:
            del self.memory_store[memory_key]

memory_manager = MemoryManager()

class PromptTemplateManager:
    @staticmethod
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

        return ChatPromptTemplate.from_messages(
            [
                ("system", f"{scenario_prompt} {difficulty_prompt}. Please ask the user a question directly without any introductory phrases.\n{{history}}"),
                ("human", "{input}")
            ]
        )

    @staticmethod
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

        return ChatPromptTemplate.from_messages(
            [
                ("system", f"{quiz_prompt} {difficulty_prompt}. Generate the quiz based on the user's selected difficulty level. Ask the quiz question directly without any introductory phrases, do not respond to the user's answer, and move immediately to the next question.\n{{history}}"),
                ("human", "{input}")
            ]
        )

class ChatService:
    @staticmethod
    def get_response(user_id, conversation_id, difficulty, scenario, user_input):
        memory = memory_manager.get_memory(user_id, conversation_id)
        # Use the default 'history' as the key expected by the prompt template
        prompt_template = PromptTemplateManager.create_chat_prompt_template(difficulty, scenario)
        conversation = ConversationChain(
            llm=bedrock_llm,
            prompt=prompt_template,
            memory=memory
        )
        return conversation.predict(input=user_input)

class QuizService:
    @staticmethod
    def get_response(user_id, conversation_id, quiz_type, difficulty, user_input):
        memory = memory_manager.get_memory(user_id, conversation_id)
        # Use the default 'history' as the key expected by the prompt template
        prompt_template = PromptTemplateManager.create_quiz_prompt_template(quiz_type, difficulty)
        conversation = ConversationChain(
            llm=bedrock_llm,
            prompt=prompt_template,
            memory=memory
        )
        return conversation.predict(input=user_input)

class S3Manager:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3', region_name='ap-northeast-1')
        self.bucket_name = bucket_name

    def save_conversation_to_s3(self, user_id, conversation_id, user_name):
        memory = memory_manager.get_memory(user_id, conversation_id)
        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in memory.chat_memory.messages
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"{user_name}/conversation_{conversation_id}_{timestamp}.txt"

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=conversation_text.encode('utf-8')
        )

        return s3_key

s3_manager = S3Manager(bucket_name='mmmybucckeet')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', '커피 주문하기')

    response = ChatService.get_response(user_id, conversation_id, difficulty, scenario, user_input)
    return jsonify({"response": response})

@app.route('/quiz', methods=['POST'])
def quiz_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')

    response = QuizService.get_response(user_id, conversation_id, quiz_type, difficulty, user_input)
    return jsonify({"response": response})

@app.route('/chat/evaluate', methods=['POST'])
def chat_evaluate_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    
    memory = memory_manager.get_memory(user_id, conversation_id)

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
    response = bedrock_llm.invoke(chat_evaluation_prompt)
    
    # 메모리 삭제
    memory_manager.delete_memory(user_id, conversation_id)
    
    return jsonify({"score": response.content})

@app.route('/quiz/evaluate', methods=['POST'])
def quiz_evaluate_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    
    memory = memory_manager.get_memory(user_id, conversation_id)

    if not memory.chat_memory.messages:
        return jsonify({"error": "No quiz history found"}), 400
    
    conversation_text = "\n".join(
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
        for message in memory.chat_memory.messages
    )
    
    feedback_prompt = f"Here is the quiz session:\n{conversation_text}\nPlease provide feedback on which answers were correct or incorrect, and suggest areas for improvement."

    response = bedrock_llm.invoke(feedback_prompt)
    
    # 메모리 삭제
    memory_manager.delete_memory(user_id, conversation_id)
    
    return jsonify({"feedback": response.content})

@app.route('/save', methods=['POST'])
def save_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')

    if not user_id or not conversation_id:
        return jsonify({"error": "User ID and conversation ID are required"}), 400

    s3_key = s3_manager.save_conversation_to_s3(user_id, conversation_id, user_name)
    return jsonify({"message": "Conversation saved", "s3_key": s3_key})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

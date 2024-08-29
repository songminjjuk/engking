from flask import Blueprint, request, jsonify
from services.chat_service import ChatService
from services.s3_manager import S3Manager

chat_bp = Blueprint('chat_bp', __name__)
s3_manager = S3Manager(bucket_name='mmmybucckeet')

@chat_bp.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('input', 'Can you ask me a question?')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', '커피 주문하기')

    response = ChatService.get_response(user_id, conversation_id, difficulty, scenario, user_input)
    return jsonify({"response": response})

@chat_bp.route('/chat/evaluate', methods=['POST'])
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
    
    memory_manager.delete_memory(user_id, conversation_id)
    
    return jsonify({"score": response.content})

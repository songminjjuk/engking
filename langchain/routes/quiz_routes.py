from flask import Blueprint, request, jsonify
from services.quiz_service import QuizService
from services.s3_manager import S3Manager

quiz_bp = Blueprint('quiz_bp', __name__)
s3_manager = S3Manager(bucket_name='mmmybucckeet')

@quiz_bp.route('/quiz', methods=['POST'])
def quiz_endpoint():
    data = request.json
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    quiz_type = data.get('quiz_type', 'vocabulary')
    difficulty = data.get('difficulty', 'Normal')
    user_input = data.get('input', 'Please give me a quiz question.')

    response = QuizService.get_response(user_id, conversation_id, quiz_type, difficulty, user_input)
    return jsonify({"response": response})

@quiz_bp.route('/quiz/evaluate', methods=['POST'])
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
    
    memory_manager.delete_memory(user_id, conversation_id)
    
    return jsonify({"feedback": response.content})

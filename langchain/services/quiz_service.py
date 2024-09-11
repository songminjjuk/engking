from modules.memory_manager import memory_manager
from modules.prompt_manager import prompt_manager
from langchain.chains import ConversationChain
from modules.bedrock_client import bedrock_llm
from fastapi.responses import JSONResponse

class QuizService:
    @staticmethod
    def process_quiz(data):
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

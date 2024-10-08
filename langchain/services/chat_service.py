from modules.memory_manager import memory_manager
from modules.prompt_manager import prompt_manager
from langchain.chains import ConversationChain
from modules.bedrock_client import bedrock_llm
from fastapi.responses import JSONResponse

class ChatService:
    @staticmethod
    def process_chat(data):
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        user_input = data.get('input', 'Can you ask me a question?')
        difficulty = data.get('difficulty', 'Normal')
        scenario = data.get('scenario', 'coffee')
        first = data.get('first', False)
        
        # logger.info(f"Request received: method={request.method}, url={request.url}, data={data}")

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

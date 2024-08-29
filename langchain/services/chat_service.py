from services.bedrock_client import BedrockClient
from services.memory_manager import MemoryManager
from services.prompt_manager import PromptTemplateManager
from langchain.chains import ConversationChain

bedrock_client = BedrockClient()
memory_manager = MemoryManager()

class ChatService:
    @staticmethod
    def get_response(user_id, conversation_id, difficulty, scenario, user_input):
        memory = memory_manager.get_memory(user_id, conversation_id)
        prompt_template = PromptTemplateManager.create_chat_prompt_template(difficulty, scenario)
        conversation = ConversationChain(
            llm=bedrock_client.get_client(),
            prompt=prompt_template,
            memory=memory
        )
        return conversation.predict(input=user_input)

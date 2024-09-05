import requests
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from config import settings

memory_store = {}

class MemoryManager:
    def get_memory(self, user_id, conversation_id):
        api_endpoint = f"{settings.DB_URL}/chatmessage/allmessages"
        request_data = {
            "memberId": user_id,
            "chatRoomId": conversation_id
        }
        response = requests.post(api_endpoint, json=request_data)
        if response.status_code == 200:
            response_data = response.json()
            memory_key = f"{user_id}_{conversation_id}"

            if memory_key not in memory_store:
                memory_store[memory_key] = ConversationBufferMemory(return_messages=True, memory_key="history")
            memory = memory_store[memory_key]

            for message in response_data:
                sender_id = message.get("senderId")
                message_text = message.get("messageText", "")

                if sender_id == "AI" and message_text:
                    memory.chat_memory.add_ai_message(AIMessage(content=message_text))
                elif message_text:
                    memory.chat_memory.add_user_message(HumanMessage(content=message_text))

            return memory
        else:
            return None

    def delete_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        if memory_key in memory_store:
            del memory_store[memory_key]

memory_manager = MemoryManager()

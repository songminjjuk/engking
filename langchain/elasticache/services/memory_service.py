# app/services/memory_service.py
import redis
from langchain.memory import ConversationBufferMemory, RedisChatMessageHistory

class MemoryService:
    def __init__(self, redis_url):
        self.redis_url = redis_url

    def get_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        chat_history = RedisChatMessageHistory(session_id=memory_key, url=self.redis_url, key_prefix="chat_history:")
        memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True, memory_key="history")
        return memory

    def delete_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        chat_history = RedisChatMessageHistory(session_id=memory_key, url=self.redis_url, key_prefix="chat_history:")
        chat_history.clear()

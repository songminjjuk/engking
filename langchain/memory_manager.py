from langchain.memory import ConversationBufferMemory

class MemoryManager:
    def __init__(self):
        self.memory_store = {}

    def get_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        if memory_key not in self.memory_store:
            self.memory_store[memory_key] = ConversationBufferMemory(return_messages=True, memory_key="history", input_key="human", output_key="ai")
        return self.memory_store[memory_key]
    
    def delete_memory(self, user_id, conversation_id):
        memory_key = f"{user_id}_{conversation_id}"
        if memory_key in self.memory_store:
            del self.memory_store[memory_key]

#####################################

# import os
# from langchain.memory import ConversationSummaryBufferMemory, RedisChatMessageHistory
# from langchain.llms.bedrock import Bedrock

# class MemoryManager:
#     def __init__(self):
#         self.redis_url = os.environ.get("ELASTICACHE_ENDPOINT_URL")

#     def get_memory(self, user_id, conversation_id):
#         memory_key = f"{user_id}_{conversation_id}"
#         chat_history = RedisChatMessageHistory(session_id=memory_key, url=self.redis_url, key_prefix="chat_history:")
        
#         # ConversationSummaryBufferMemory는 이전 대화의 요약을 유지하는 데 사용됩니다.
#         llm = self.get_llm()
#         memory = ConversationSummaryBufferMemory(
#             ai_prefix="AI Assistant",
#             llm=llm,
#             max_token_limit=1024,
#             chat_memory=chat_history
#         )
#         return memory

#     def delete_memory(self, user_id, conversation_id):
#         memory_key = f"{user_id}_{conversation_id}"
#         chat_history = RedisChatMessageHistory(session_id=memory_key, url=self.redis_url, key_prefix="chat_history:")
#         chat_history.clear()  # Redis에서 해당 대화 기록 삭제

#     def get_llm(self):
#         model_kwargs = {
#             "max_tokens_to_sample": 8000,
#             "temperature": 0,
#             "top_k": 50,
#             "top_p": 1,
#             "stop_sequences": ["\n\nHuman:"]
#         }
#         llm = Bedrock(
#             credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"),
#             region_name=os.environ.get("BWB_REGION_NAME"),
#             endpoint_url=os.environ.get("BWB_ENDPOINT_URL"),
#             model_id="anthropic.claude-v2",
#             model_kwargs=model_kwargs
#         )
#         return llm

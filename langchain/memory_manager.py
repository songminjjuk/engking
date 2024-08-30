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

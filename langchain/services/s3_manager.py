import boto3
from datetime import datetime
from services.memory_manager import MemoryManager
from langchain.schema import HumanMessage

class S3Manager:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3', region_name='ap-northeast-1')
        self.bucket_name = bucket_name
        self.memory_manager = MemoryManager()

    def save_conversation_to_s3(self, user_id, conversation_id, user_name):
        memory = self.memory_manager.get_memory(user_id, conversation_id)
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

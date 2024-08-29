from config import bedrock_llm

class BedrockClient:
    def __init__(self):
        self.client = bedrock_llm

    def get_client(self):
        return self.client

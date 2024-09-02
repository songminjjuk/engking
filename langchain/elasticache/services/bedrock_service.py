# app/services/bedrock_service.py
import boto3
from langchain_aws import ChatBedrock

class BedrockService:
    def __init__(self, model_id, region_name):
        self.bedrock_llm = ChatBedrock(
            model_id=model_id,
            model_kwargs=dict(temperature=0),
            region_name=region_name,
            streaming=True,
            client=boto3.client("bedrock-runtime", region_name=region_name)
        )

    def get_llm(self):
        return self.bedrock_llm

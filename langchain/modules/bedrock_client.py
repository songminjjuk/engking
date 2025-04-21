import boto3
from langchain_aws import ChatBedrock
from config import settings

def initialize_bedrock_client(model_id, region_name):
    return ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0.5),
        region_name=region_name,
        streaming=True,
        client=boto3.client("bedrock-runtime", region_name=region_name)
    )

bedrock_llm = initialize_bedrock_client(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    #model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    region_name=settings.AWS_REGION
)
bedrock_llm2 = initialize_bedrock_client(
    model_id = "anthropic.claude-3-haiku-20240307-v1:0",
    region_name=settings.AWS_REGION
)

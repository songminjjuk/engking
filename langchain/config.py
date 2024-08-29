import boto3
from langchain_aws import ChatBedrock

def initialize_bedrock_client(model_id, region_name):
    return ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0),
        region_name=region_name,
        client=boto3.client("bedrock-runtime", region_name=region_name)
    )

S3_BUCKET_NAME = 'mmmybucckeet'
bedrock_llm = initialize_bedrock_client(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="ap-northeast-1"
)

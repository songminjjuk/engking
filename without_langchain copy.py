import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="ap-northeast-1")
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

prompt_template = "Tell me a short joke about {topic}"

def call_chat_model(messages: list) -> str:
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": messages,
    }

    request = json.dumps(native_request)
    response = bedrock.invoke_model(modelId=model_id, body=request)
    response_body = json.loads(response["body"])
    
    return response_body["streaming_response"][0]["text"]

def invoke_chain(topic: str) -> str:
    prompt_value = prompt_template.format(topic=topic)
    messages = [{"role": "user", "content": prompt_value}]
    return call_chat_model(messages)

print(invoke_chain("ice cream"))

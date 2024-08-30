import boto3
from langchain_aws import ChatBedrock

class BedrockClient:
    def __init__(self, model_id, region_name):
        self.client = ChatBedrock(
            model_id=model_id,
            model_kwargs=dict(temperature=0),
            region_name=region_name,
            streaming=True,
            client=boto3.client("bedrock-runtime", region_name=region_name)
        )

    def invoke(self, prompt):
        return self.client.invoke(prompt)

    async def stream_invoke(self, prompt):
        async for chunk in self.client.astream(prompt):
            yield chunk.content

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import boto3
from langchain_aws import ChatBedrock


memory_store = {}

# Bedrock LLM 초기화
def initialize_bedrock_client(model_id, region_name):
    return ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0),
        region_name=region_name,
        streaming=True,  # 스트리밍을 활성화
        client=boto3.client("bedrock-runtime", region_name=region_name)
    )

bedrock_llm = initialize_bedrock_client(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="ap-northeast-1"
)

def get_memory(user_id, conversation_id):
    memory_key = f"{user_id}_{conversation_id}"
    if memory_key not in memory_store:
        memory_store[memory_key] = ConversationBufferMemory(return_messages=True)
    return memory_store[memory_key]

# 프롬프트 템플릿 정의
prompt = PromptTemplate(
    input_variables=["human_input", "chat_history"],
    template="Chat_History: {chat_history}\nHuman: {human_input}\nAI:"
)

# ConversationBufferMemory 초기화
memory = ConversationBufferMemory(
    input_key="human_input", 
    output_key="ai_response",
    memory_key="chat_history"
)

# 스트리밍 응답을 위한 함수
async def stream_response(human_input):
    # 메모리에서 대화 기록을 불러옵니다.
    chat_history = memory.load_memory_variables({}).get("chat_history", "")

    # 프롬프트를 생성합니다.
    prompt_text = prompt.format(human_input=human_input, chat_history=chat_history)
    
    # 메시지를 스트리밍 방식으로 처리합니다.
    full_response = ""
    async for chunk in bedrock_llm.astream(prompt_text):
        response_content = chunk.content
        print(response_content, end="", flush=True)
        yield response_content
        full_response += response_content  # 전체 응답을 누적합니다.
    
    # 새로운 대화 내용을 메모리에 저장합니다.
    memory.save_context({"human_input": human_input}, {"ai_response": full_response})

# 실행 및 스트리밍 출력
import asyncio

async def main():
    async for response in stream_response("안녕하세요!"):
        pass

# asyncio를 사용하여 비동기 함수 실행
asyncio.run(main())

# 저장된 대화 내용 확인
print(memory.load_memory_variables({}))

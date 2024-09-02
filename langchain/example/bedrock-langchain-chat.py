import streamlit as st
import boto3
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate

# Claude 모델을 초기화 (ChatBedrock 사용)
bedrock_llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",  # 확인된 모델 ID를 사용하세요.
    model_kwargs=dict(temperature=0),
    region_name="ap-northeast-1",
    client=boto3.client("bedrock-runtime", region_name="ap-northeast-1")
)

# 대화를 위한 프롬프트 템플릿 정의
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ]
)

# 프롬프트와 모델을 연결
chain = prompt_template | bedrock_llm

# Streamlit 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI 설정
st.title("Claude와 대화할뢔?")

# 이전 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input("What is up?")
if user_input:
    # 사용자 입력을 세션 상태에 저장
    st.session_state.messages.append({"role": "human", "content": user_input})

    # 사용자 메시지 표시
    with st.chat_message("human"):
        st.markdown(user_input)

    # Claude와의 대화를 통해 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # 체인 실행하여 응답 받기
        response = chain.invoke({"input": user_input})

        # 응답에서 텍스트만 추출하기
        full_response = response.content if hasattr(response, "content") else str(response)

        message_placeholder.markdown(full_response)

    # 어시스턴트 응답을 세션 상태에 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})
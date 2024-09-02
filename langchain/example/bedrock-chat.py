import streamlit as st
import boto3
import json

client = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

model_id = "anthropic.claude-3-haiku-20240307-v1:0"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("대화하기")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("What is up?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        prompt = user_input

        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        request = json.dumps(native_request)

        streaming_response = client.invoke_model_with_response_stream(
            modelId=model_id, body=request
        )

        for event in streaming_response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                chunk_text = chunk["delta"].get("text", "")
                full_response += chunk_text
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

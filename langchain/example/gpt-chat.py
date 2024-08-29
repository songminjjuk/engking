import streamlit as st
from openai import OpenAI
import os
os.environ["OPENAI_API_KEY"] = "sk-WJu8cZr88lTKabomd5F52NfIdb7CApzTQd-g3kH2OeT3BlbkFJNZjQszTK1eyNtd0Qx1-cAoq4ASkXxoEHTTMUQ-zB0A"
client = OpenAI()

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
        for response in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
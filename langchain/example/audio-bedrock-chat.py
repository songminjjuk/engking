import base64
import streamlit as st
import boto3
import json
import requests
from datetime import datetime
from audio_recorder_streamlit import audio_recorder

# AWS 클라이언트 생성
transcribe = boto3.client('transcribe', region_name="ap-northeast-1")
polly = boto3.client('polly', region_name="ap-northeast-1")
bedrock = boto3.client("bedrock-runtime", region_name="ap-northeast-1")
s3 = boto3.client('s3', region_name="ap-northeast-1")
bucket_name = "mmmybucckeet"
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_file_name(prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def save_text_to_s3(text, bucket, key):
    s3.put_object(Body=text, Bucket=bucket, Key=key)

def upload_to_s3(file_path, bucket, key):
    s3.upload_file(file_path, bucket, key)
    s3_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    return s3_url

def generate_job_name():
    return f"transcribe-job-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def transcribe_audio(file_path, file_name):
    # S3에 파일 업로드
    s3_key = "input_audio/" + file_name  # input_audio_YYYYMMDD_HHMMSS.mp3 형식으로 파일명 지정
    job_uri = upload_to_s3(file_path, bucket_name, s3_key)

    job_name = generate_job_name()
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',  # input_audio의 format
        LanguageCode='en-US'
    )

    # 트랜스크립션 작업 완료 대기 (간단한 방식으로 폴링)
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        st.spinner("Transcribing audio... Please wait.")

    if result['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_file_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_response = requests.get(transcript_file_uri)
        transcript_text = transcript_response.json()['results']['transcripts'][0]['transcript']
        
        # 텍스트 데이터를 S3에 저장 (input_text/ 폴더에 input_text_YYYYMMDD_HHMMSS.txt 형태로 저장)
        transcript_key = "input_text/" + file_name.replace("input_audio", "input_text").replace(".mp3", ".txt")
        save_text_to_s3(transcript_text, bucket_name, transcript_key)
        
        return transcript_text

def text_to_speech(text, output_file_name):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',  # output_audio의 format
        VoiceId='Joanna'  # 원하는 목소리 선택
    )

    # 로컬 파일에 음성 저장
    local_file_path = output_file_name
    with open(local_file_path, 'wb') as file:
        file.write(response['AudioStream'].read())

    # S3에 음성 파일 업로드
    output_s3_key = "output_audio/" + output_file_name
    upload_to_s3(local_file_path, bucket_name, output_s3_key)
    
    return local_file_path

st.title("Claude와 음성 채팅하기")

con1 = st.container()
con2 = st.container()

user_input = ""

with con2:
    audio_bytes = audio_recorder("말씀하세요", pause_threshold=3.0)
    try:
        if audio_bytes:
            # 로컬 및 S3에 저장될 파일 이름 생성 (input_audio_YYYYMMDD_HHMMSS.mp3)
            audio_file_name = generate_file_name("input_audio", "mp3")
            
            # 로컬에 음성 파일 저장
            with open(audio_file_name, "wb") as f:
                f.write(audio_bytes)

            # S3에 업로드 및 Transcribe 호출
            user_input = transcribe_audio(audio_file_name, audio_file_name)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

with con1:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Claude 모델에 질문
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
            streaming_response = bedrock.invoke_model_with_response_stream(
                modelId=model_id, body=request
            )

            for event in streaming_response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if chunk["type"] == "content_block_delta":
                    chunk_text = chunk["delta"].get("text", "")
                    full_response += chunk_text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # Bedrock 응답 텍스트를 S3에 저장 (output_text/ 폴더에 output_text_YYYYMMDD_HHMMSS.txt 형태로 저장)
            response_text_key = "output_text/" + audio_file_name.replace("input_audio", "output_text").replace(".mp3", ".txt")
            save_text_to_s3(full_response, bucket_name, response_text_key)

            # 응답을 음성으로 변환하고 S3에 업로드 (output_audio/ 폴더에 output_audio_YYYYMMDD_HHMMSS.mp3 형태로 저장)
            output_audio_file_name = audio_file_name.replace("input_audio", "output_audio")
            speech_file_path = text_to_speech(full_response, output_audio_file_name)
            autoplay_audio(speech_file_path)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

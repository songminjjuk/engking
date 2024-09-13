# app/modules/polly.py
import os
from app.modules.s3 import save_audio_to_s3
from app.modules.common import get_boto3_client

# AWS 서비스 클라이언트 생성
polly = get_boto3_client('polly')

def synthesize_speech(text, filename):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'  # 원하는 음성으로 변경 가능
    )
    
    audio_stream = response['AudioStream'].read()

    # S3에 파일 저장
    audio_s3_url = save_audio_to_s3(filename, audio_stream)

    return audio_s3_url

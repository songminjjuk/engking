# app/modules/polly.py
import boto3
import os

from app.modules.s3 import save_audio_to_s3

# AWS 인증 정보 설정
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
region_name = os.getenv('REGION_NAME')

polly = boto3.client(
    'polly',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

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

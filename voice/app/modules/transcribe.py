# app/modules/transcribe.py
import boto3
import os
import time
import requests

from app.modules.s3 import get_full_path

# 환경 변수 체크
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
region_name = os.getenv('REGION_NAME')
bucket_name = os.getenv('BUCKET_NAME')

if not all([aws_access_key_id, aws_secret_access_key, region_name, bucket_name]):
    raise ValueError("AWS credentials or bucket name are not set in environment variables.")

transcribe = boto3.client(
    'transcribe',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

async def transcribe_audio(filename: str):
    job_name = "transcription_job_" + str(int(time.time()))

    # filename = presigned_url.split('?')[0].split('/')[-1]

    s3_uri = f"s3://{bucket_name}/{get_full_path(filename)}"

    try:
        # 전사 작업 시작
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat='mp3',
            LanguageCode='en-US'
        )
    except Exception as e:
        raise Exception(f"Failed to start transcription job: {e}")

    # 작업 상태 확인
    while True:
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)

        if response['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(1)

    if response['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']

    # requests를 사용하여 JSON 데이터 다운로드
    response = requests.get(transcript_uri)
    if response.status_code != 200:
        raise Exception(f"Failed to download transcript: {response.text}")

    # JSON 데이터로 변환
    transcript_data = response.json()
    if 'results' in transcript_data and 'transcripts' in transcript_data['results']:
        transcript_text = transcript_data['results']['transcripts'][0]['transcript']
        return transcript_text
    else:
        raise Exception("Invalid transcript data format.")

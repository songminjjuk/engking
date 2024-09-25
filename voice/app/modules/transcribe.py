import os
import time
import requests
from app.modules.common import get_boto3_client
from app.modules.s3 import get_full_path, check_if_object_exists

region_name = os.getenv('REGION_NAME')
bucket_name = os.getenv('BUCKET_NAME')

if not all([region_name, bucket_name]):
    raise ValueError("AWS region name or bucket name are not set in environment variables.")

# Transcribe 클라이언트 생성
transcribe = get_boto3_client('transcribe')

async def transcribe_audio(filename: str):
    # S3에 파일이 존재하는지 확인
    if not check_if_object_exists(bucket_name, filename):
        raise Exception(f"파일이 S3 버킷에 존재하지 않습니다: {filename}")

    job_name = "transcription_job_" + str(int(time.time()))
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

import boto3
import time
import requests

def transcribe_audio(file_path, bucket_name, file_name):
    # AWS 클라이언트 생성
    s3 = boto3.client('s3')
    transcribe = boto3.client('transcribe')

    # S3에 파일 업로드
    s3_key = "input_audio/" + file_name  # input_audio/ 디렉토리에 파일 업로드
    s3.upload_file(file_path, bucket_name, s3_key)
    job_uri = f"s3://{bucket_name}/{s3_key}"

    # Transcribe 작업 시작
    job_name = "transcribe-job-" + str(int(time.time()))
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',  # 오디오 파일의 형식에 따라 변경 가능 (예: 'wav', 'flac')
        LanguageCode='en-US'
    )

    # 트랜스크립션 작업 완료 대기
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        if status in ['COMPLETED', 'FAILED']:
            break
        print("Transcribing... Please wait.")
        time.sleep(5)  # 5초마다 상태 확인

    if status == 'COMPLETED':
        transcript_file_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_response = requests.get(transcript_file_uri)
        transcript_text = transcript_response.json()['results']['transcripts'][0]['transcript']
        print("Transcription completed.")
        print("Transcribed Text:", transcript_text)
        return transcript_text
    else:
        print("Transcription failed.")
        return None

# 사용 예시
file_path = "sample2.flac"  # 로컬 파일 경로
bucket_name = "mmmybucckeet"  # S3 버킷 이름
file_name = "sample2.flac"  # S3에 저장할 파일 이름

transcribed_text = transcribe_audio(file_path, bucket_name, file_name)

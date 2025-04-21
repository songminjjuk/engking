# import boto3
# import time
# import requests

# def transcribe_audio(file_path, bucket_name, file_name):
#     # AWS 클라이언트 생성
#     s3 = boto3.client('s3')
#     transcribe = boto3.client('transcribe')

#     # S3에 파일 업로드
#     s3_key = "input_audio/" + file_name  # input_audio/ 디렉토리에 파일 업로드
#     s3.upload_file(file_path, bucket_name, s3_key)
#     job_uri = f"s3://{bucket_name}/{s3_key}"

#     # Transcribe 작업 시작
#     job_name = "transcribe-job-" + str(int(time.time()))
#     transcribe.start_transcription_job(
#         TranscriptionJobName=job_name,
#         Media={'MediaFileUri': job_uri},
#         MediaFormat='mp3',  # 오디오 파일의 형식에 따라 변경 가능 (예: 'wav', 'flac')
#         LanguageCode='en-US'
#     )

#     # 트랜스크립션 작업 완료 대기
#     while True:
#         result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
#         status = result['TranscriptionJob']['TranscriptionJobStatus']
#         if status in ['COMPLETED', 'FAILED']:
#             break
#         print("Transcribing... Please wait.")
#         time.sleep(5)  # 5초마다 상태 확인

#     if status == 'COMPLETED':
#         transcript_file_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
#         transcript_response = requests.get(transcript_file_uri)
#         transcript_text = transcript_response.json()['results']['transcripts'][0]['transcript']
#         print("Transcription completed.")
#         print("Transcribed Text:", transcript_text)
#         return transcript_text
#     else:
#         print("Transcription failed.")
#         return None

# # 사용 예시
# file_path = "sample2.flac"  # 로컬 파일 경로
# bucket_name = "mmmybucckeet"  # S3 버킷 이름
# file_name = "sample2.flac"  # S3에 저장할 파일 이름

# transcribed_text = transcribe_audio(file_path, bucket_name, file_name)
import boto3
import time
import requests
import jiwer  # WER 계산을 위한 라이브러리
import datetime

def transcribe_audio(file_path, bucket_name, file_name, reference_text=None):
    # AWS 클라이언트 생성
    s3 = boto3.client('s3')
    transcribe = boto3.client('transcribe')

    # S3에 파일 업로드
    s3_key = "input_audio/" + file_name  # input_audio/ 디렉토리에 파일 업로드
    s3.upload_file(file_path, bucket_name, s3_key)
    job_uri = f"s3://{bucket_name}/{s3_key}"

    # Transcribe 작업 시작
    job_name = "transcribe-job-" + str(int(time.time()))
    start_time = time.time()  # 작업 시작 시간 측정
    print(f"Starting transcription job: {job_name}")

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
        time.sleep(0.1) 

    end_time = time.time()  # 작업 완료 시간 측정
    execution_time = end_time - start_time  # 총 실행 시간

    if status == 'COMPLETED':
        transcript_file_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_response = requests.get(transcript_file_uri)
        transcript_text = transcript_response.json()['results']['transcripts'][0]['transcript']
        print("Transcription completed.")
        print("Transcribed Text:", transcript_text)
        print(f"Execution time: {str(datetime.timedelta(seconds=execution_time))}")

        # WER 계산 (참고 텍스트가 있을 경우)
        if reference_text:
            wer = jiwer.wer(reference_text, transcript_text)
            print(f"Word Error Rate (WER): {wer * 100:.2f}%")
        return transcript_text
    else:
        print("Transcription failed.")
        return None

# 사용 예시
file_path = "sample2.flac"  # 로컬 파일 경로
bucket_name = "minseok-transcribe-test"  # S3 버킷 이름
file_name = "sample2.flac"  # S3에 저장할 파일 이름
reference_text = "before he had time to answer a much-encumbered vera burst into the room with the question i say can i leave these here these were a small black pig and a lusty specimen of black-red game-cock"  # 참고 텍스트

transcribed_text = transcribe_audio(file_path, bucket_name, file_name, reference_text)

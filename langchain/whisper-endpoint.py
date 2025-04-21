import boto3
import json
import time
import jiwer  # WER 계산을 위한 라이브러리
import datetime

reference_text = ("before he had time to answer a much-encumbered vera burst into the room "
                  "with the question i say can i leave these here these were a small black pig "
                  "and a lusty specimen of black-red game-cock")

# SageMaker Runtime 클라이언트 생성
runtime = boto3.client('runtime.sagemaker')

# 이미 배포된 엔드포인트 이름
endpoint_name = "hf-asr-whisper-large-v3-2024-10-17-09-57-41-978"  # 배포된 엔드포인트 이름

def transcribe_audio(audio_file_name):
    # 오디오 파일 불러오기
    with open(audio_file_name, "rb") as file:
        audio_data = file.read()

    # API 호출 (STT 요청)
    start_time = time.time()  # 실행 시간 측정 시작
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="audio/wav",  # 오디오 형식에 맞게 수정 (예: 'audio/flac', 'audio/mpeg')
        Body=audio_data
    )
    end_time = time.time()  # 실행 시간 측정 종료

    # 결과 처리
    result = json.loads(response['Body'].read().decode())
    transcribed_text = result.get('text', '')  # 트랜스크립션 결과

    # 출력
    print(f"Transcribed Text: {transcribed_text}")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")

    # WER 계산 (참고 텍스트와 트랜스크립션된 텍스트 비교)
    wer = jiwer.wer(reference_text, transcribed_text)
    print(f"Word Error Rate (WER): {wer * 100:.2f}%")
    return transcribed_text

# 사용 예시
audio_file_name = "sample2.flac"  # 오디오 파일 경로
transcribed_text = transcribe_audio(audio_file_name)
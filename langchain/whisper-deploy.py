import boto3
import json
import time
from sagemaker.jumpstart import utils
from sagemaker.jumpstart.model import JumpStartModel
import jiwer  # WER 계산을 위한 라이브러리
import datetime

# 참고 텍스트
reference_text = ("before he had time to answer a much-encumbered vera burst into the room "
                  "with the question i say can i leave these here these were a small black pig "
                  "and a lusty specimen of black-red game-cock")

# Whisper 모델 ID
model_id = "huggingface-asr-whisper-large-v3"
# model_id = "huggingface-asr-whisper-small"

# JumpStart를 사용해 모델 배포
role = "arn:aws:iam::355627705292:role/SageMakerFullAccess"
model = JumpStartModel(model_id=model_id, role=role)
predictor = model.deploy(instance_type="ml.g5.xlarge")

# SageMaker 엔드포인트 이름
endpoint_name = predictor.endpoint_name
print(f"Model deployed at endpoint: {endpoint_name}")

# SageMaker Runtime 클라이언트 생성
runtime = boto3.client('runtime.sagemaker')

# 오디오 파일 불러오기
audio_file_name = "sample2.flac"
with open(audio_file_name, "rb") as file:
    audio_data = file.read()

# 실행 시간 측정 시작
start_time = time.time()

# API 호출
response = runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="audio/wav",  # 오디오 형식에 맞게 변경 (예: 'audio/flac', 'audio/mpeg')
    Body=audio_data
)

# 실행 시간 측정 종료
end_time = time.time()
execution_time = end_time - start_time  # 실행 시간 계산

# 결과 처리
result = json.loads(response['Body'].read().decode())
transcribed_text = result.get('text', '')  # 트랜스크립션 결과 텍스트

# 출력
print(f"Transcribed Text: {transcribed_text}")
print(f"Execution Time: {str(datetime.timedelta(seconds=execution_time))}")

# WER 계산 (참고 텍스트와 트랜스크립션된 텍스트 비교)
wer = jiwer.wer(reference_text, transcribed_text)
print(f"Word Error Rate (WER): {wer * 100:.2f}%")

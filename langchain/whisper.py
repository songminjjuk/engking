import boto3
import json
from sagemaker.jumpstart import utils
from sagemaker.jumpstart.model import JumpStartModel

model_id = "huggingface-asr-whisper-large-v3"

# JumpStart를 사용해 모델 배포
role = "arn:aws:iam::261595668962:role/SageMakerFullAccess"
model = JumpStartModel(model_id=model_id, role=role)
predictor = model.deploy()

# SageMaker 엔드포인트 이름
endpoint_name = predictor.endpoint_name
print(f"Model deployed at endpoint: {endpoint_name}")

# SageMaker Runtime 클라이언트 생성
runtime = boto3.client('runtime.sagemaker')

# 오디오 파일 불러오기
audio_file_name = "sample2.flac"
with open(audio_file_name, "rb") as file:
    audio_data = file.read()

# API 호출
response = runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="audio/wav",
    Body=audio_data
)

# 결과 처리
result = json.loads(response['Body'].read().decode())
print(result)

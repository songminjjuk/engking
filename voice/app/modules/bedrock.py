# app/modules/bedrock.py
import boto3
import os
import random

# 환경 변수에서 S3 버킷 이름 로드
BUCKET_NAME = os.getenv('BUCKET_NAME')

s3_client = boto3.client('s3')

def generate_unique_filename(base_name):
    """기본 이름을 바탕으로 겹치지 않는 파일명 생성"""
    filename = base_name
    counter = 1

    # 파일이 존재하는지 확인
    while check_if_object_exists(BUCKET_NAME, filename):
        filename = f"{base_name.split('.')[0]}_{counter}.{base_name.split('.')[-1]}"
        counter += 1

    return filename

def check_if_object_exists(bucket_name, object_name):
    """S3에서 객체 존재 여부 확인"""
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_name)
        return True
    except Exception:
        return False

async def send_to_bedrock(text):
    # 실제 API 호출 대신 랜덤한 결과를 생성하는 모의 함수로 대체
    mock_responses = [
        {"result": "This is a test response.", "new_filename": "test_response.mp3", "memberId": "temp_member_1"},
        {"result": "Another response returned from Bedrock.", "new_filename": "another_response.mp3", "memberId": "temp_member_2"},
        {"result": "Temporary message for testing purposes.", "new_filename": "temp_response.mp3", "memberId": "temp_member_3"}
    ]

    # 랜덤하게 모의 응답 선택
    return random.choice(mock_responses)

    # Uncomment below to use actual API when ready
    # response = requests.post(BEDROCK_URL, json={"text": text})
    # if response.status_code == 200:
    #     return response.json().get('result', {})


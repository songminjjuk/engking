import boto3
import os
from botocore.config import Config  # Config를 임포트합니다.

# AWS 인증 정보 설정
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('REGION_NAME')

# 기본 Config 설정
default_config = Config(signature_version='v4')

def get_boto3_client(service_name: str):
    """
    주어진 서비스 이름에 대한 Boto3 클라이언트를 반환합니다.
    
    :param service_name: 사용할 AWS 서비스 이름 (예: 's3', 'ec2', 등)
    :return: Boto3 클라이언트
    """
    # Boto3 클라이언트 생성
    if aws_access_key_id and aws_secret_access_key:
        return boto3.client(
            service_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            config=default_config  # 기본 Config 사용
        )
    else:
        # IAM Role을 사용하는 경우
        return boto3.client(
            service_name,
            region_name=region_name,
            config=default_config  # 기본 Config 사용
        )

def generate_unique_filename(member_id: str, chat_room_id: str, message_id: str) -> str:
    """고유한 파일명을 생성하는 함수"""
    return f"{member_id}/{chat_room_id}/{message_id}.mp3"  # 파일명 포맷

# app/modules/s3.py
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Literal

# AWS 인증 정보 설정
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
bucket_name = os.getenv('BUCKET_NAME')
region_name = os.getenv('REGION_NAME')

s3_client = boto3.client(
    's3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

def get_full_path(filename: str):
    return f"audio/{filename}"

def check_if_object_exists(bucket_name: str, filename: str) -> bool:
    full_path = get_full_path(filename)

    try:
        s3_client.head_object(Bucket=bucket_name, Key=full_path)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e

def generate_presigned_url(filename: str, operation: Literal['put_object', 'get_object']):
    full_path = get_full_path(filename)
    try:
        # presigned URL 생성
        response = s3_client.generate_presigned_url(
            operation,  # 'put_object' 또는 'get_object'로 설정
            Params={'Bucket': bucket_name, 'Key': full_path},
            ExpiresIn=3600  # 유효 기간 (초)
        )
        return response
    except NoCredentialsError:
        print("AWS 자격 증명이 잘못되었습니다.")
        return None
    except ClientError as e:
        print(f"Client error while generating presigned URL: {e}")
        return None
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

def save_audio_to_s3(filename: str, audio_content: bytes):
    try:
        full_path = get_full_path(filename)

        # presigned URL 생성
        presigned_url = generate_presigned_url(filename, 'get_object')
        
        # 객체 존재 여부 체크
        if check_if_object_exists(bucket_name, filename):
            print(f"객체 '{full_path}'가 이미 존재합니다. presigned URL을 반환합니다.")
            return presigned_url
        
        # S3에 파일 저장 (Content-Type을 audio/mpeg로 설정)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=full_path,
            Body=audio_content,
            ContentType='audio/mpeg'  # Content-Type 설정
        )
        
        return presigned_url
    except NoCredentialsError:
        print("AWS 자격 증명이 잘못되었습니다.")
        return None
    except ClientError as e:
        print(f"Client error while saving audio to S3: {e}")
        return None
    except Exception as e:
        print(f"Error saving audio to S3: {e}")
        return None


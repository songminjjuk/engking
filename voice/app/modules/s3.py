import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Literal
from botocore.config import Config

# AWS 인증 정보 설정
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = os.getenv('BUCKET_NAME')
region_name = os.getenv('REGION_NAME')

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    # endpoint_url=f'https://{bucket_name}.s3.{region_name}.amazonaws.com',
    #config=Config(signature_version='s3v4'),
    region_name=region_name
)
# ep = s3_client.meta.endpoint_url
# print("ep: ",ep)

def get_full_path(filename: str) -> str:
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

    httpMethod = 'PUT' if operation == 'put_object' else 'GET'
    
    try:
        # presigned URL 생성
        params = {'Bucket': bucket_name, 'Key': full_path}

        response = s3_client.generate_presigned_url(
            ClientMethod=operation,
            Params=params,
            HttpMethod=httpMethod,
            ExpiresIn=3600
        )
        return response

        modified_url = f'https://{bucket_name}.s3.{region_name}.amazonaws.com/{full_path}?{response.split("?")[1]}'.replace(f'{bucket_name}/', "")
        print(modified_url)
        return modified_url
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

        # if check_if_object_exists(bucket_name, filename):
        #     print(f"객체 '{full_path}'가 이미 존재합니다. presigned URL을 반환합니다.")
        #     return generate_presigned_url(filename, 'get_object')

        # S3에 파일 저장
        s3_client.put_object(
            Bucket=bucket_name,
            Key=full_path,
            Body=audio_content,
            # ContentType='audio/mpeg'
        )

        return generate_presigned_url(filename, 'get_object')
    except NoCredentialsError:
        print("AWS 자격 증명이 잘못되었습니다.")
        return None
    except ClientError as e:
        print(f"Client error while saving audio to S3: {e}")
        return None
    except Exception as e:
        print(f"Error saving audio to S3: {e}")
        return None

def generate_presigned_post(filename: str):
    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=filename,
            ExpiresIn=3600,
            Conditions=[
                {"acl": "public-read"},
                ["starts-with", "$Content-Type", ""]
            ],
            Fields={"acl": "public-read", "Content-Type": "application/octet-stream"}
        )
        return response
    except NoCredentialsError:
        raise Exception("AWS credentials not found.")
    except Exception as e:
        raise Exception(f"Error generating presigned POST: {str(e)}")

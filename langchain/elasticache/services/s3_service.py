# app/services/s3_service.py
import boto3
from datetime import datetime

class S3Service:
    def __init__(self, bucket_name, region_name):
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.bucket_name = bucket_name

    def save_conversation(self, user_name, conversation_id, conversation_text):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"{user_name}/conversation_{conversation_id}_{timestamp}.txt"
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=conversation_text.encode('utf-8')
        )
        return s3_key

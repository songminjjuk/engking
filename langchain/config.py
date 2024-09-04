# from pydantic import BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    DB_URL: str
    # S3_BUCKET_NAME: str
    AWS_REGION: str

    class Config:
        env_file = ".env"

# 환경 변수 인스턴스
settings = Settings()

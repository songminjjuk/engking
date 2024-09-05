from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    DB_URL: str
    AWS_REGION: str

    class Config:
        env_file = ".env"

settings = Settings()

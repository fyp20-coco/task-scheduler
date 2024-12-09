import os
from dotenv import load_dotenv
from pydantic import BaseSettings




load_dotenv()
class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "Coco Task Scheduler"

    class Config:
        env_file = ".env"

settings = Settings()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
GOOGLE_SCOPES= os.getenv('GOOGLE_SCOPES').split(',')

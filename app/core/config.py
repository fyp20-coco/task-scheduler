import os
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings




load_dotenv()
class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "Coco Task Scheduler"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    # GOOGLE_SCOPES: List[str]

    class Config:
        env_file = ".env"

    # @property
    # def GOOGLE_SCOPES(self) -> List[str]:
    #     return self._GOOGLE_SCOPES.split(",")    

settings = Settings()

# Access variables as attributes of `settings`
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI
# GOOGLE_SCOPES = settings.GOOGLE_SCOPES


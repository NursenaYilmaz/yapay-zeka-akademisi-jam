from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()  # .env dosyasını oku

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "default")

def get_settings():
    return Settings()

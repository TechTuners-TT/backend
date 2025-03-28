from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")

settings = Settings()
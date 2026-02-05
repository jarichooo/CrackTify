"""Configuration management for the app"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    APP_TITLE = "Cracktify"

    API_BASE_URL = os.getenv("API_BASE_URL")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")

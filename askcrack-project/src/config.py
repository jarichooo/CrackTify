"""Configuration management for the app"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    APP_TITLE = 'Cracktify'

    APP_WIDTH = 540
    APP_HEIGHT = 960

    API_BASE_URL = os.getenv("API_BASE_URL")
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "data", "app_database.db")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")

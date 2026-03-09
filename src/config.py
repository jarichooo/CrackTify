"""Configuration management for the app"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    APP_TITLE = "Cracktify"
    API_BASE_URL = os.getenv("API_BASE_URL")

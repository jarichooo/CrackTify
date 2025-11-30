"""Configuration management for the app"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    APP_TITLE = 'AskCrack'

    APP_WIDTH = 540
    APP_HEIGHT = 960
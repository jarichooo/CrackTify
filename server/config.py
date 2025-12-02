import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # SQLAlchemy connection string
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Email settings
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secretjwtkey")
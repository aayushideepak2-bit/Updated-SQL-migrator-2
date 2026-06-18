import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration for Flask, SQLAlchemy, and JWT."""
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-jwt-secret-key")
    
    # Use in-memory SQLite database for now to avoid file path issues on Windows
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///:memory:"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv(
        "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
    ).lower() in ["true", "1", "yes"]

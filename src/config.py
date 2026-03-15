from dotenv import load_dotenv
import os
from datetime import timedelta
from pathlib import Path

# Load environment variables from .env
load_dotenv(dotenv_path="./.env")

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

class Config(object):
    SECRET_KEY = os.getenv("MY_SECRET_KEY", "default_secret_key")
    BASE_DIR = BASE_DIR
    TEMPLATES_FOLDERS = "src/templates"

    RESTX_MASK_SWAGGER = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLite database file
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=12)

    AUTHORIZATION = {
        "JsonWebToken": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }

    MAIL_SERVER = os.getenv("MAIL_SERVER", "MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT", "MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "MAIL_PASSWORD")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

    # Separate SQLite DB for tests
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'test.sqlite3'}"
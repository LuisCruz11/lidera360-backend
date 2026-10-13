import os
from datetime import timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
    BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Lidera360")
    EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", 10))

    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://lidera360-frontend.onrender.com").rstrip("/")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HORAS", 8))
    )

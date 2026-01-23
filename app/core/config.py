import os
from dotenv import load_dotenv

load_dotenv()


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


class Settings:
    ENV = env("ENV", "dev")

    DATABASE_URL = env("DATABASE_URL")  # Supabase Postgres connection string

    JWT_SECRET = env("JWT_SECRET", "change-me")
    JWT_ALG = env("JWT_ALG", "HS256")
    ACCESS_TOKEN_MINUTES = int(env("ACCESS_TOKEN_MINUTES", "30"))
    REFRESH_TOKEN_DAYS = int(env("REFRESH_TOKEN_DAYS", "14"))

    # Cloudflare R2 (optional right now)
    R2_ENDPOINT_URL = env("R2_ENDPOINT_URL")
    R2_ACCESS_KEY_ID = env("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = env("R2_SECRET_ACCESS_KEY")
    R2_BUCKET = env("R2_BUCKET")
    R2_PUBLIC_BASE_URL = env("R2_PUBLIC_BASE_URL")  # if bucket is public


settings = Settings()

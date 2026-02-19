from pydantic_settings import BaseSettings
import os


class Config(BaseSettings):
    SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:5432/{os.getenv("POSTGRES_DB")}"




settings = Config()






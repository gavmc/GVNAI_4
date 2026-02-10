from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GVNAI"

    BACKEND_CORS_ORIGIN: List[AnyHttpUrl] = []
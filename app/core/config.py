from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from typing import List, Union, Optional


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GVNAI"

    BACKEND_CORS_ORIGIN: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGIN", mode="before")
    @classmethod
    def assemble_cors_origin(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "gvnai"
    DATABASE_URL: Optional[str] = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    AGENT_MAX_ITERATIONS: int = 15
    AGENT_TIMEOUT_SECONDS: int = 120

    ENCRYPTION_KEY: str = "generate-a-fernet-key-for-production"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
import os
from enum import Enum

from pydantic import BaseSettings, Field


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_URL: str
    STARKBANK_USER_PRIVATE_KEY: str = Field(default=open("tls/private-key.pem").read(),
                                            validation_alias="STARKBANK_USER_PRIVATE_KEY")
    STARKBANK_PROJECT_ID: str
    ENVIRONMENT: Environment = Environment.DEVELOPMENT


settings = Settings()

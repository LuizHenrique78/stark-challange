import os
from enum import Enum

from pydantic import BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_URL: str
    STARKBANK_USER_PRIVATE_KEY: str = open("app/tls/private-key.pem").read()
    STARKBANK_PROJECT_ID: str
    ENVIRONMENT: Environment = Environment.DEVELOPMENT


settings = Settings()

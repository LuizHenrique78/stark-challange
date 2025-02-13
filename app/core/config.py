import os
from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    STAGING = "test"


class Settings(BaseSettings):
    DATABASE_URL: str = Field("default")
    RABBITMQ_URL: str = Field("default")
    STARKBANK_USER_PRIVATE_KEY: str = Field("default")
    STARKBANK_PROJECT_ID: str
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_local_environment()

    def setup_local_environment(self):
        """Set environment local variables."""
        if self.ENVIRONMENT == Environment.DEVELOPMENT:
            self.STARKBANK_USER_PRIVATE_KEY = open("tls/private-key.pem").read()
            self.DATABASE_URL = "postgresql://postgres:exemple@localhost:5432/mydb"
            self.RABBITMQ_URL = "amqp://user:pass@localhost:5672"


settings = Settings()

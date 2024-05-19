"""Configuration module for importing environmental variables"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseAwsSettings(BaseSettings):
    """Base settings for AWS Client"""

    aws_access_key_id: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region: str | None = os.getenv("AWS_REGION")

    model_config = SettingsConfigDict(case_sensitive=True)


class CognitoSettings(BaseAwsSettings):
    """Settings for Congito User Pool Client"""

    user_pool_id: str | None = os.getenv("USER_POOL_ID")
    app_client_id: str | None = os.getenv("APP_CLIENT_ID")
    app_client_secret: str | None = os.getenv("APP_CLIENT_SECRET")

    model_config = SettingsConfigDict(case_sensitive=True)

from paths import PATH_ROOT
from pydantic_settings import BaseSettings


class CoreConfig(BaseSettings):
    """db-ally configuration"""

    pg_connection_string: str = "postgresql://developer:EzB9rIF%5E%25fF8jKM4@35.205.190.141:5432"
    openai_api_key: str = "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"

    class Config:
        """Config for env class."""

        env_file = str(PATH_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"


config = CoreConfig()

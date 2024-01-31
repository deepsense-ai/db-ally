from paths import PATH_ROOT
from pydantic_settings import BaseSettings


class CoreConfig(BaseSettings):
    """db-ally configuration"""

    pg_connection_string: str

    class Config:
        """Config for env class."""

        env_file = str(PATH_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"


config = CoreConfig()

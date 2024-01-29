from pydantic_settings import BaseSettings

from dbally.paths import PATH_ROOT


class CoreConfig(BaseSettings):
    """db-ally configuration"""

    database_conn_string: str = ""

    class Config:
        """Config for env class."""

        env_file = str(PATH_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"


config = CoreConfig()

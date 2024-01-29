from pydantic.v1 import BaseSettings

from dbally.paths import PATH_ROOT


class BenchmarkConfig(BaseSettings):
    """db-ally Benchmark configuration."""

    neptune_project: str = "deepsense-ai/db-ally"
    neptune_api_token: str = ""
    openai_api_key: str = ""

    class Config:
        """Config for env class."""

        env_file = PATH_ROOT / ".env"
        env_file_encoding = "utf-8"


config = BenchmarkConfig()

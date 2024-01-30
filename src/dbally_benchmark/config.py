from pydantic.v1 import BaseSettings

from dbally.constants import GenerationModelType
from dbally_benchmark.paths import PATH_PACKAGE


class BenchmarkConfig(BaseSettings):
    """db-ally Benchmark configuration."""

    pg_conn_string: str = ""

    generation_model_type: GenerationModelType = GenerationModelType.GPT4

    neptune_project: str = "deepsense-ai/db-ally"
    neptune_api_token: str = ""

    class Config:
        """Config for env class."""

        env_file = str(PATH_PACKAGE / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"


config = BenchmarkConfig()

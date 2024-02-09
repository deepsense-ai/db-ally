from pydantic.v1 import BaseSettings

from dbally_benchmark.paths import PATH_PACKAGE


class BenchmarkConfig(BaseSettings):
    """db-ally Benchmark configuration."""

    pg_conn_string: str = "postgresql://developer:EzB9rIF%5E%25fF8jKM4@35.205.190.141:5432" + "/superhero"
    openai_api_key: str = "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"
    model_name: str = "gpt-3.5"

    neptune_project: str = "deepsense-ai/db-ally"
    neptune_api_token: str = "eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiJmNjU5NmRkNi1mMGRmLTQ3NzgtOTlhNS1mMTcwYWU5MzIyMTMifQ=="

    class Config:
        """Config for env class."""

        env_file = str(PATH_PACKAGE / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"


config = BenchmarkConfig()

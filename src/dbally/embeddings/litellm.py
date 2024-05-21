from typing import Dict, List, Optional

try:
    import litellm

    HAVE_LITELLM = True
except ImportError:
    HAVE_LITELLM = False

from dbally.embeddings.base import EmbeddingClient

from ._exceptions import EmbeddingConnectionError, EmbeddingResponseError, EmbeddingStatusError


class LiteLLMEmbeddingClient(EmbeddingClient):
    """
    Client for creating text embeddings using LiteLLM API.
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        options: Optional[Dict] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        """
        Constructs the LiteLLMEmbeddingClient.

        Args:
            model: Name of the [LiteLLM supported model](https://docs.litellm.ai/docs/embedding/supported_embedding)\
                to be used. Default is "text-embedding-3-small".
            options: Additional options to pass to the LiteLLM API.
            api_base: The API endpoint you want to call the model with.
            api_key: API key to be used. API key to be used. If not specified, an environment variable will be used,
                for more information, follow the instructions for your specific vendor in the\
                [LiteLLM documentation](https://docs.litellm.ai/docs/embedding/supported_embedding).
            api_version: The API version for the call.

        Raises:
            ImportError: If the litellm package is not installed.
        """
        if not HAVE_LITELLM:
            raise ImportError("You need to install litellm package to use LiteLLM models")

        super().__init__()
        self.model = model
        self.options = options or {}
        self.api_base = api_base
        self.api_key = api_key
        self.api_version = api_version

    async def get_embeddings(self, data: List[str]) -> List[List[float]]:
        """
        Creates embeddings for the given strings.

        Args:
            data: List of strings to get embeddings for.

        Returns:
            List of embeddings for the given strings.

        Raises:
            EmbeddingConnectionError: If there is a connection error with the embedding API.
            EmbeddingStatusError: If the embedding API returns an error status code.
            EmbeddingResponseError: If the embedding API response is invalid.
        """
        try:
            response = await litellm.aembedding(
                input=data,
                model=self.model,
                api_base=self.api_base,
                api_key=self.api_key,
                api_version=self.api_version,
                **self.options,
            )
        except litellm.openai.APIConnectionError as exc:
            raise EmbeddingConnectionError() from exc
        except litellm.openai.APIStatusError as exc:
            raise EmbeddingStatusError(exc.message, exc.status_code) from exc
        except litellm.openai.APIResponseValidationError as exc:
            raise EmbeddingResponseError() from exc

        return [embedding["embedding"] for embedding in response.data]

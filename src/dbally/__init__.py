""" dbally """

from dbally.data_models.execution_result import ExecutionResult
from dbally.views import decorators
from dbally.views.methods_base import MethodsBaseView
from dbally.views.pandas_base import DataFrameBaseView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView
from dbally.views.structured import BaseStructuredView

from .__version__ import __version__
from ._main import create_collection, create_multicollection
from ._types import NOT_GIVEN, NotGiven
from .collection import Collection
from .embeddings.exceptions import (
    EmbeddingConnectionError,
    EmbeddingError,
    EmbeddingResponseError,
    EmbeddingStatusError,
)
from .exceptions import DbAllyError
from .llms.clients.exceptions import LLMConnectionError, LLMError, LLMResponseError, LLMStatusError

__all__ = [
    "__version__",
    "create_collection",
    "create_multicollection",
    "decorators",
    "MethodsBaseView",
    "SqlAlchemyBaseView",
    "Collection",
    "MultiCollection",
    "BaseStructuredView",
    "DataFrameBaseView",
    "ExecutionResult",
    "DbAllyError",
    "EmbeddingError",
    "EmbeddingConnectionError",
    "EmbeddingResponseError",
    "EmbeddingStatusError",
    "LLMError",
    "LLMConnectionError",
    "LLMResponseError",
    "LLMStatusError",
    "NotGiven",
    "NOT_GIVEN",
]

from .multicollection import MultiCollection

# Update the __module__ attribute for exported symbols so that
# error messages point to this module instead of the module
# it was originally defined in, e.g.
# dbally._exceptions.LLMError -> dbally.LLMError
__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        try:
            __locals[__name].__module__ = "dbally"
        except (TypeError, AttributeError):
            # Some of our exported symbols are builtins which we can't set attributes for.
            pass

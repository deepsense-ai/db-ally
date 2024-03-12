from .index import AbstractSimilarityIndex, SimilarityIndex
from .sqlalchemy_base import SimpleSqlAlchemyFetcher
from .store import AbstractStore

# depends on the faiss package
try:
    from .faiss_store import FaissStore
except ImportError:
    pass

__all__ = [
    "AbstractSimilarityIndex",
    "SimilarityIndex",
    "SimpleSqlAlchemyFetcher",
    "AbstractStore",
    "FaissStore",
]

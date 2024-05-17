from .fetcher import SimilarityFetcher
from .index import AbstractSimilarityIndex, SimilarityIndex
from .sqlalchemy_base import SimpleSqlAlchemyFetcher, SqlAlchemyFetcher
from .store import SimilarityStore

# depends on the faiss package

try:
    from .faiss_store import FaissStore
except ImportError:
    pass

try:
    from .chroma_store import ChromadbStore
except ImportError:
    pass

try:
    from .elastic_store import ElasticStore
except ImportError:
    pass

__all__ = [
    "AbstractSimilarityIndex",
    "SimilarityIndex",
    "SqlAlchemyFetcher",
    "SimpleSqlAlchemyFetcher",
    "SimilarityStore",
    "SimilarityFetcher",
    "FaissStore",
    "ElasticStore",
    "ChromadbStore",
]

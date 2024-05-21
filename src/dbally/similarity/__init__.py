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
    from .elasticsearch_store import ElasticsearchStore
except ImportError:
    pass

try:
    from .elastic_vector_search import ElasticVectorStore
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
    "ElasticsearchStore",
    "ElasticVectorStore",
    "ChromadbStore",
]

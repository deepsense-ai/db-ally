from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np

from dbally.embeddings.base import EmbeddingClient
from dbally.similarity.store import SimilarityStore


class FaissStore(SimilarityStore):
    """
    The FaissStore class stores text embeddings using Meta Faiss.
    """

    def __init__(
        self,
        index_dir: str,
        index_name: str,
        embedding_client: EmbeddingClient,
        max_distance: Optional[float] = None,
        index_type: faiss.IndexFlat = faiss.IndexFlatL2,
    ) -> None:
        """
        Initializes the FaissStore.

        Args:
            index_dir: The directory to store the index file.
            index_name: The name of the index.
            max_distance: The maximum distance between two text embeddings to be considered similar.
            embedding_client: The client to use for creating text embeddings.
            index_type: The type of Faiss index to use. Defaults to faiss.IndexFlatL2. See
                [Faiss wiki](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes) for more information.
        """
        super().__init__()
        self.index_dir = index_dir
        self.index_name = index_name
        self.max_distance = max_distance
        self.embedding_client = embedding_client
        self.index_type = index_type

    def get_index_path(self, create: bool = False) -> Path:
        """
        Returns the path to the index file.

        Args:
            create: If True, the directory will be created if it does not exist.

        Returns:
            Path: The path to the index file.
        """
        directory = Path(self.index_dir)
        if create:
            directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{self.index_name}.index"

    async def store(self, data: List[str]) -> None:
        """
        Stores the data in a faiss index on disk.

        Args:
            data: The data to store.
        """

        # Store embeddings in faiss index on disk
        embeddings = np.array(await self.embedding_client.get_embeddings(data), dtype=np.float32)
        index = self.index_type(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, str(self.get_index_path(create=True)))

        # Save data to be able to retrieve the most similar text
        with open(self.get_index_path(create=True).with_suffix(".npy"), "wb") as file:
            np.save(file, np.array(data, dtype="str"))

    async def find_similar(self, text: str) -> Optional[str]:
        """
        Finds the most similar text in the store or returns None if no similar text is found.

        Args:
            text: The text to find similar to.

        Returns:
            The most similar text or None if no similar text is found.
        """
        index = faiss.read_index(str(self.get_index_path()))
        embedding = np.array(await self.embedding_client.get_embeddings([text]), dtype=np.float32)
        scores, similar = index.search(embedding, 1)
        best_distance, best_idx = scores[0][0], similar[0][0]

        if best_idx != -1 and (self.max_distance is None or best_distance <= self.max_distance):
            with open(self.get_index_path().with_suffix(".npy"), "rb") as file:
                data = np.load(file)
                return data[best_idx]
        return None

    def __repr__(self) -> str:
        """
        Returns the string representation of the FaissStore.

        Returns:
            str: The string representation of the FaissStore.
        """
        return f"{self.__class__.__name__}(index_dir={self.index_dir}, index_name={self.index_name})"

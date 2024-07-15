from typing import List

from faiss.swigfaiss import IndexFlatL2

from dbally.embeddings.litellm import LiteLLMEmbeddingClient
from dbally.similarity.faiss_store import FaissStore
from dbally.similarity.index import SimilarityIndex
from dbally.views.freeform.text2sql.config import ColumnConfig, TableConfig
from dbally.views.freeform.text2sql.view import BaseText2SQLView


class SuperheroFreeformView(BaseText2SQLView):
    """
    Freeform view for the Superhero SQLite database.
    """

    def get_tables(self) -> List[TableConfig]:
        """
        Get the tables used by the view.

        Returns:
            The list of tables used by the view.
        """
        return [
            TableConfig(
                name="alignment",
                columns=[
                    ColumnConfig(
                        name="alignment",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("alignment", "alignment"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="alignment_alignment_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The 'alignment' table is a simple reference table storing different types of
                    moral alignments (such as Good, Bad, Neutral or N/A). Each alignment type is
                    assigned a unique identifier.""",
            ),
            TableConfig(
                name="attribute",
                columns=[
                    ColumnConfig(
                        name="attribute_name",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("attribute", "attribute_name"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="attribute_attribute_name_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The table named 'attribute' is used to store various attributes like
                    intelligence, strength, speed, durability, power, etc. Each attribute is
                    uniquely identified by an ID.""",
            ),
            TableConfig(
                name="colour",
                columns=[
                    ColumnConfig(
                        name="colour",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("colour", "colour"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="colour_colour_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The "colour" table in the SQLite database is a simple lookup table consisting of
                    colour names. Each entry in the table has a unique identifier and associated
                    text representing different colours.""",
            ),
            TableConfig(
                name="gender",
                columns=[
                    ColumnConfig(
                        name="gender",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("gender", "gender"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="gender_gender_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The table named 'gender' is designed to store gender information. Each record
                    consists of an integer identifier and its corresponding gender which may be
                    'Male', 'Female' or 'N/A'.""",
            ),
            TableConfig(
                name="publisher",
                columns=[
                    ColumnConfig(
                        name="publisher_name",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("publisher", "publisher_name"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="publisher_publisher_name_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The "publisher" table stores information pertaining to various publishers. Each
                    entry consists of a unique ID and the name of the publisher. Some entries
                    may not have a publisher name.""",
            ),
            TableConfig(
                name="race",
                columns=[
                    ColumnConfig(
                        name="race",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("race", "race"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="race_race_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The 'race' table associates a unique ID to different races which can include
                    various categories including clarifications such as "-" or specific types
                    like "Alien", "Alpha", "Amazon", "Android" etc.""",
            ),
            TableConfig(
                name="superpower",
                columns=[
                    ColumnConfig(
                        name="power_name",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("superpower", "power_name"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="superpower_power_name_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The "superpower" table stores a list of different superpowers. Each superpower
                    has a unique identifier and a name.""",
            ),
            TableConfig(
                name="superhero",
                columns=[
                    ColumnConfig(
                        name="superhero_name",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("superhero", "superhero_name"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="superhero_superhero_name_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                    ColumnConfig(
                        name="full_name",
                        data_type="TEXT",
                        description=None,
                        similarity_index=SimilarityIndex(
                            fetcher=self._create_default_fetcher("superhero", "full_name"),
                            store=FaissStore(
                                index_dir=".",
                                index_name="superhero_full_name_index",
                                embedding_client=LiteLLMEmbeddingClient(
                                    model="text-embedding-3-small",
                                    options={},
                                    api_base=None,
                                    api_key=None,
                                    api_version=None,
                                ),
                                max_distance=None,
                                index_type=IndexFlatL2,
                            ),
                        ),
                    ),
                ],
                description="""The "superhero" table holds information about various superheroes. This includes
                    their superhero name, their full name, and other descriptive characteristics
                    like their gender, eye, hair, and skin color, race, height, and weight. Each
                    of these descriptive characteristics has an associated id that corresponds
                    to a particular description. The alignment and publisher of the superhero
                    are also included in this table. The table is linked with multiple other
                    tables such as 'alignment', 'colour', 'gender', 'publisher', 'race' via
                    foreign key constraints.""",
            ),
            TableConfig(
                name="hero_attribute",
                columns=[],
                description="""The "hero_attribute" table is a join table that connects superheroes and their
                    attributes. It has foreign keys referring to the ID of the hero from the
                    "superhero" table and the ID of the attribute from the "attribute" table. It
                    also stores the values for these hero attributes.""",
            ),
            TableConfig(
                name="hero_power",
                columns=[],
                description="""The 'hero_power' table is a relational junction table that links superheros
                    ('hero_id') with their corresponding superpowers ('power_id'). This table
                    exhibits a many-to-many relationship between superheros and superpowers,
                    indicating that a single superhero can have multiple superpowers, and
                    similarly, a single superpower can be attributed to multiple superheros. The
                    'hero_id' and 'power_id' are foreign keys that reference the primary keys in
                    the 'superhero' and 'superpower' tables respectively.""",
            ),
        ]

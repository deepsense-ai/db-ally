from abc import ABC
from typing import Dict, List, Tuple

import pytest
from chromadb import PersistentClient
from sqlalchemy import ColumnClause, MetaData, Table, create_engine

from dbally.embeddings.litellm import LiteLLMEmbeddingClient
from dbally.similarity.chroma_store import ChromadbStore
from dbally.similarity.index import SimilarityIndex
from dbally.similarity.sqlalchemy_base import SimpleSqlAlchemyFetcher
from dbally.views.freeform.text2sql.config import ColumnConfig, TableConfig
from dbally_codegen.generator import CodeGenerator, Text2SQLViewGenerator


class MockGenerator(CodeGenerator):
    def generate(self) -> str:
        ...


class MockClass:
    def mock_method1(param1: int, param2: str = "default") -> None:
        pass

    def mock_method2(param1, param2: str) -> List[str]:
        pass

    def mock_method3(param1: int, param2: str):
        pass


@pytest.fixture
def generator() -> MockGenerator:
    return MockGenerator()


@pytest.fixture
def text2sql_view_generator() -> Text2SQLViewGenerator:
    return Text2SQLViewGenerator([])


def test_group_imports(generator: MockGenerator) -> None:
    generator.imports = {
        "os": {"path"},
        "sys": {"version"},
        "pytest": {"fixture"},
    }
    grouped_imports = generator.group_imports()
    expected = [
        [
            "from os import path",
            "from sys import version",
        ],
        [
            "from pytest import fixture",
        ],
    ]
    assert grouped_imports == expected


def test_collect_imports_for_annotation(generator: MockGenerator) -> None:
    generator.collect_imports_for_annotation(int)
    generator.collect_imports_for_annotation(List[int])
    generator.collect_imports_for_annotation(Tuple[str, str, Dict[str, float]])
    assert generator.imports == {"typing": {"Dict", "List", "Tuple"}}


def test_collect_imports_for_method(generator: MockGenerator) -> None:
    generator.collect_imports_for_method(MockClass.mock_method1)
    generator.collect_imports_for_method(MockClass.mock_method2)
    generator.collect_imports_for_method(MockClass.mock_method3)
    assert generator.imports == {"typing": {"List"}}


def test_render_annotation(generator: MockGenerator) -> None:
    assert generator.render_annotation(int) == "int"
    assert generator.render_annotation(List[int]) == "List[int]"
    assert generator.render_annotation(Tuple[str, str, Dict[str, float]]) == "Tuple[str, str, Dict[str, float]]"


def test_render_class_declaration_no_parents(generator: MockGenerator) -> None:
    assert generator.render_class_declaration("MyClass") == "class MyClass:"
    assert generator.render_class_declaration("MyClass", [ABC]) == "class MyClass(ABC):"
    assert generator.render_class_declaration("MyClass", [ABC, MockClass]) == "class MyClass(ABC, MockClass):"


def test_render_method(generator: MockGenerator) -> None:
    assert (
        generator.render_method(MockClass.mock_method1, "pass")
        == 'def mock_method1(param1: int, param2: str = "default") -> None:\n    pass'
    )
    assert (
        generator.render_method(MockClass.mock_method2, "...")
        == "def mock_method2(param1, param2: str) -> List[str]:\n    ..."
    )
    assert (
        generator.render_method(MockClass.mock_method3, "...") == "def mock_method3(param1: int, param2: str):\n    ..."
    )


def test_collect_imports_for_view(text2sql_view_generator: Text2SQLViewGenerator) -> None:
    text2sql_view_generator.tables = [
        TableConfig(
            name="candidate",
            columns=[
                ColumnConfig(
                    name="id",
                    data_type="VARCHAR",
                ),
                ColumnConfig(
                    name="tags",
                    data_type="VARCHAR",
                    description=None,
                    similarity_index=SimilarityIndex(
                        fetcher=SimpleSqlAlchemyFetcher(
                            sqlalchemy_engine=create_engine("sqlite://"),
                            column=ColumnClause("candidate"),
                            table=Table("tags", MetaData()),
                        ),
                        store=ChromadbStore(
                            index_name="candidate_tags_index",
                            chroma_client=PersistentClient(),
                            embedding_function=LiteLLMEmbeddingClient(),
                        ),
                    ),
                ),
            ],
        ),
    ]
    text2sql_view_generator.collect_imports_for_view()
    assert text2sql_view_generator.imports == {
        "typing": {"List"},
        "dbally.views.freeform.text2sql.view": {"BaseText2SQLView"},
        "dbally.views.freeform.text2sql.config": {"TableConfig", "ColumnConfig"},
        "dbally.similarity.index": {"SimilarityIndex"},
        "dbally.similarity.chroma_store": {"ChromadbStore"},
        "dbally.embeddings.litellm": {"LiteLLMEmbeddingClient"},
        "chromadb.api.client": {"Client"},
    }


def test_render_view(text2sql_view_generator: Text2SQLViewGenerator) -> None:
    text2sql_view_generator.tables = [
        TableConfig(
            name="candidate",
            columns=[
                ColumnConfig(
                    name="id",
                    data_type="VARCHAR",
                ),
                ColumnConfig(
                    name="tags",
                    data_type="VARCHAR",
                    description=None,
                    similarity_index=SimilarityIndex(
                        fetcher=SimpleSqlAlchemyFetcher(
                            sqlalchemy_engine=create_engine("sqlite://"),
                            column=ColumnClause("candidate"),
                            table=Table("tags", MetaData()),
                        ),
                        store=ChromadbStore(
                            index_name="candidate_tags_index",
                            chroma_client=PersistentClient(),
                            embedding_function=LiteLLMEmbeddingClient(),
                        ),
                    ),
                ),
            ],
        ),
    ]
    code = text2sql_view_generator.generate()
    assert code == (
        "from dbally.embeddings.litellm import LiteLLMEmbeddingClient\n"
        "from dbally.similarity.chroma_store import ChromadbStore\n"
        "from dbally.similarity.index import SimilarityIndex\n"
        "from dbally.views.freeform.text2sql.config import ColumnConfig, TableConfig\n"
        "from dbally.views.freeform.text2sql.view import BaseText2SQLView\n"
        "from typing import List\n\n"
        "from chromadb.api.client import Client\n\n"
        "class Text2SQLView(BaseText2SQLView):\n"
        "    def get_tables(self) -> List[TableConfig]:\n"
        "        return [\n"
        "            TableConfig(\n"
        '                name="candidate",\n'
        "                columns=[\n"
        "                    ColumnConfig(\n"
        '                        name="id",\n'
        '                        data_type="VARCHAR",\n'
        "                        description=None,\n"
        "                        similarity_index=None,\n"
        "                    ),\n"
        "                    ColumnConfig(\n"
        '                        name="tags",\n'
        '                        data_type="VARCHAR",\n'
        "                        description=None,\n"
        "                        similarity_index=SimilarityIndex(\n"
        '                            fetcher=self._create_default_fetcher("candidate", "tags"),\n'
        "                            store=ChromadbStore(\n"
        '                                index_name="candidate_tags_index",\n'
        "                                chroma_client=Client(\n"
        '                                    tenant="default_tenant",\n'
        '                                    database="default_database",\n'
        "                                ),\n"
        "                                embedding_function=LiteLLMEmbeddingClient(\n"
        '                                    model="text-embedding-3-small",\n'
        "                                    options={},\n"
        "                                    api_base=None,\n"
        "                                    api_key=None,\n"
        "                                    api_version=None,\n"
        "                                ),\n"
        "                                max_distance=None,\n"
        "                            ),\n"
        "                        ),\n"
        "                    ),\n"
        "                ],\n"
        "                description=None,\n"
        "            ),\n"
        "        ]\n"
    )

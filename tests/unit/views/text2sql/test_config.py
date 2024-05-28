import tempfile
from pathlib import Path

from dbally_codegen.config import Text2SQLConfig, Text2SQLTableConfig


def test_text2sql_config_persistence():
    config = Text2SQLConfig(
        tables={
            "table1": Text2SQLTableConfig(
                ddl="SAMPLE DDL1", description="SAMPLE DESCRIPTION1", similarity={"col1": "SEMANTIC", "col2": "TRIGRAM"}
            ),
            "table2": Text2SQLTableConfig(
                ddl="SAMPLE DDL2", description="SAMPLE DESCRIPTION2", similarity={"col3": "SEMANTIC", "col4": "TRIGRAM"}
            ),
        }
    )

    with tempfile.NamedTemporaryFile() as f:
        config.to_file(Path(f.name))
        loaded_config = Text2SQLConfig.from_file(Path(f.name))

    assert len(config.tables) == len(loaded_config.tables)

    table1 = loaded_config.tables["table1"]
    assert table1.ddl == "SAMPLE DDL1"
    assert table1.description == "SAMPLE DESCRIPTION1"
    assert table1.similarity == {"col1": "SEMANTIC", "col2": "TRIGRAM"}

    table2 = loaded_config.tables["table2"]
    assert table2.ddl == "SAMPLE DDL2"
    assert table2.description == "SAMPLE DESCRIPTION2"
    assert table2.similarity == {"col3": "SEMANTIC", "col4": "TRIGRAM"}

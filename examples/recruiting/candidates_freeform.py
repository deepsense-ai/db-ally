# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

from dbally.views.freeform.text2sql import BaseText2SQLView, ColumnConfig, TableConfig

engine = create_engine("sqlite:///examples/recruiting/data/candidates.db")

_Base = automap_base()
_Base.prepare(autoload_with=engine)
_Candidate = _Base.classes.candidates


class CandidateFreeformView(BaseText2SQLView):
    """
    A view for retrieving candidates from the database.
    """

    def get_tables(self) -> List[TableConfig]:
        """
        Get the tables used by the view.

        Returns:
            A list of tables.
        """
        return [
            TableConfig(
                name="candidates",
                columns=[
                    ColumnConfig("name", "TEXT"),
                    ColumnConfig("country", "TEXT"),
                    ColumnConfig("years_of_experience", "INTEGER"),
                    ColumnConfig("position", "TEXT"),
                    ColumnConfig("university", "TEXT"),
                    ColumnConfig("skills", "TEXT"),
                    ColumnConfig("tags", "TEXT"),
                    ColumnConfig("id", "INTEGER PRIMARY KEY"),
                ],
            ),
        ]

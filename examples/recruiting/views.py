from datetime import date
from typing import List, Literal

import awoc  # pip install a-world-of-countries
import sqlalchemy
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, select

from dbally import SqlAlchemyBaseView, decorators
from dbally.prompt.elements import FewShotExample

from .db import Candidate


class RecruitmentView(SqlAlchemyBaseView):
    """
    A view for the recruitment database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.

        Returns:
            sqlalchemy.Select: A select object.
        """
        return select(Candidate)

    @decorators.view_filter()
    def at_least_experience(self, years: int) -> sqlalchemy.ColumnElement:  # pylint: disable=W0602, C0116, W9011
        return Candidate.years_of_experience >= years

    @decorators.view_filter()
    def has_seniority(  # pylint: disable=W0602, C0116, W9011
        self, seniority: Literal["junior", "senior", "mid"]
    ) -> sqlalchemy.ColumnElement:
        if seniority == "junior":
            return Candidate.years_of_experience < 2
        if seniority == "mid":
            return Candidate.years_of_experience < 5

        return Candidate.years_of_experience >= 5

    @decorators.view_filter()
    def data_scientist_position(self) -> sqlalchemy.ColumnElement:  # pylint: disable=W0602, C0116, W9011
        """Defines a perfect candidate for data scientist position."""
        return and_(
            Candidate.position.in_(["Data Scientist", "Machine Learning Engineer"]),
            Candidate.years_of_experience >= 3,
        )

    @decorators.view_filter()
    def is_from_continent(  # pylint: disable=W0602, C0116, W9011
        self, continent: Literal["Europe", "Asia", "Africa", "North America", "South America", "Australia"]
    ) -> sqlalchemy.ColumnElement:
        my_world = awoc.AWOC()
        wanted_countries = my_world.get_countries_list_of(continent)
        return Candidate.country.in_(wanted_countries)

    @decorators.view_filter()
    def studied_at(self, university: str) -> sqlalchemy.ColumnElement:  # pylint: disable=W0602, C0116, W9011
        return Candidate.university == university


class FewShotRecruitmentView(RecruitmentView):
    """
    A view for the recruitment database including examples of question:answers pairs (few-shot).
    """

    @decorators.view_filter()
    def is_available_within_months(  # pylint: disable=W0602, C0116, W9011
        self, months: int
    ) -> sqlalchemy.ColumnElement:
        start = date.today()
        end = start + relativedelta(months=months)
        return Candidate.available_from.between(start, end)

    def list_few_shots(self) -> List[FewShotExample]:  # pylint: disable=W9011, C0116
        return [
            FewShotExample(
                "Which candidates studied at University of Toronto?",
                'studied_at("University of Toronto")',
            ),
            FewShotExample(
                "Do we have any soon available candidate?",
                lambda: self.is_available_within_months(1),
            ),
            FewShotExample(
                "Do we have any soon available perfect fits for senior data scientist positions?",
                lambda: (
                    self.is_available_within_months(1)
                    and self.data_scientist_position()
                    and self.has_seniority("senior")
                ),
            ),
            FewShotExample(
                "List all junior or senior data scientist positions",
                lambda: (
                    self.data_scientist_position() and (self.has_seniority("junior") or self.has_seniority("senior"))
                ),
            ),
        ]

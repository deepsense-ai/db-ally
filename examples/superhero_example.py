# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc
import asyncio

import pandas as pd
import sqlalchemy
from config import config
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

import dbally
from dbally import SqlAlchemyBaseView, decorators

engine = create_engine(config.pg_connection_string + "/superhero")
SuperheroModel = automap_base()
SuperheroModel.prepare(autoload_with=engine, reflect=True)


class SuperheroFilterMixin:
    @decorators.view_filter()
    def filter_by_superhero_name(self, name: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.superhero_name == name

    @decorators.view_filter()
    def filter_by_eye_color(self, color: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.eye_colour_id.in_(
            sqlalchemy.select(SuperheroModel.classes.colour.id).where(SuperheroModel.classes.colour.colour == color)
        )

    @decorators.view_filter()
    def filter_by_hair_color(self, color: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.hair_colour_id.in_(
            sqlalchemy.select(SuperheroModel.classes.colour.id).where(SuperheroModel.classes.colour.colour == color)
        )

    @decorators.view_filter()
    def filter_by_skin_color(self, color: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.skin_colour_id.in_(
            sqlalchemy.select(SuperheroModel.classes.colour.id).where(SuperheroModel.classes.colour.colour == color)
        )

    @decorators.view_filter()
    def filter_by_race(self, race: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.race_id.in_(
            sqlalchemy.select(SuperheroModel.classes.race.id).where(SuperheroModel.classes.race.race == race)
        )

    @decorators.view_filter()
    def filter_by_publisher(self, publisher: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.publisher_id.in_(
            sqlalchemy.select(SuperheroModel.classes.publisher.id).where(
                SuperheroModel.classes.publisher.publisher == publisher
            )
        )

    @decorators.view_filter()
    def filter_by_alignment(self, alignment: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.alignment_id.in_(
            sqlalchemy.select(SuperheroModel.classes.alignment.id).where(
                SuperheroModel.classes.alignment.alignment == alignment
            )
        )

    @decorators.view_filter()
    def filter_by_gender(self, gender: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.gender_id.in_(
            sqlalchemy.select(SuperheroModel.classes.gender.id).where(SuperheroModel.classes.gender.gender == gender)
        )

    @decorators.view_filter()
    def heavier_than(self, weight: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.weight_kg > weight

    @decorators.view_filter()
    def lighter_than(self, weight: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.weight_kg < weight

    @decorators.view_filter()
    def taller_than(self, height: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.height_cm > height


class SuperheroView(SqlAlchemyBaseView, SuperheroFilterMixin):
    """
    Main view, meant for finding superheroes meeting specific criteria
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return sqlalchemy.select(SuperheroModel.classes.superhero)

    @decorators.view_action()
    def sort_by_gender(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        return select.order_by(SuperheroModel.classes.superhero.gender_id)


# todo: sometimes I use classes, sometimes metadata.tables, because some classes aren't automapped correctly.
# at some point we should either fix the automap or use metadata.tables everywhere
class SuperheroCountByPowerView(SuperheroView, SuperheroFilterMixin):
    """
    View used to count the number of superheroes with a specific power.
    """

    def __init__(self) -> None:
        self._superhero_count = sqlalchemy.func.count(SuperheroModel.classes.superhero.id).label("superhero_count")
        super().__init__()

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        hero_power = SuperheroModel.metadata.tables["hero_power"]
        return (
            sqlalchemy.select(
                SuperheroModel.classes.superpower.power_name,
                self._superhero_count,
            )
            .join(hero_power, hero_power.c.hero_id == SuperheroModel.classes.superhero.id)
            .join(SuperheroModel.classes.superpower, SuperheroModel.classes.superpower.id == hero_power.c.power_id)
            .group_by(SuperheroModel.classes.superpower.power_name)
        )

    @decorators.view_action()
    def sort_by_superhero_count_ascending(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        return select.order_by(self._superhero_count.asc())

    @decorators.view_action()
    def sort_by_superhero_count_descending(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        return select.order_by(self._superhero_count.desc())


async def main():
    dbally.use_openai_llm(
        model_name="gpt-4",
        openai_api_key=config.openai_api_key,  # You can pass key directly or just have OPENAI_API_KEY env var defined.
    )

    superheros_db = dbally.create_collection("superheros_db")
    superheros_db.add(SuperheroView)
    superheros_db.add(SuperheroCountByPowerView)

    response = await superheros_db.ask("What heroes have blue eyes and are taller than 180.5cm?")
    print(response)
    print(pd.read_sql_query(response, engine))

    response = await superheros_db.ask("Count power of female heros")
    print(response)
    print(pd.read_sql_query(response, engine))


if __name__ == "__main__":
    asyncio.run(main())

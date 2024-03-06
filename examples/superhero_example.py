# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc, duplicate-code
import asyncio

import sqlalchemy
from config import config
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import aliased

import dbally
from dbally import SqlAlchemyBaseView, decorators
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.similarity.index import SimilarityIndex
from dbally.similarity.sqlalchemy_base import CaseInsensitiveSqlAlchemyStore, SimpleSqlAlchemyFetcher

engine = create_engine(config.pg_connection_string + "/superhero")
SuperheroModel = automap_base()
SuperheroModel.prepare(autoload_with=engine, reflect=True)

eye_color_alias = aliased(SuperheroModel.classes.colour)
hair_color_alias = aliased(SuperheroModel.classes.colour)
skin_color_alias = aliased(SuperheroModel.classes.colour)

hero_power = SuperheroModel.metadata.tables["hero_power"]
hero_attr = SuperheroModel.metadata.tables["hero_attribute"]


class SuperheroDBSchema:
    id = SuperheroModel.classes.superhero.id
    name = SuperheroModel.classes.superhero.superhero_name
    full_name = SuperheroModel.classes.superhero.full_name
    gender = SuperheroModel.classes.gender.gender
    race = SuperheroModel.classes.race.race
    publisher_name = SuperheroModel.classes.publisher.publisher_name
    alignment = SuperheroModel.classes.alignment.alignment
    weight_kg = SuperheroModel.classes.superhero.weight_kg
    height_cm = SuperheroModel.classes.superhero.height_cm
    eye_color = eye_color_alias.colour.label("eye_color")
    hair_color = hair_color_alias.colour.label("hair_color")
    skin_color = skin_color_alias.colour.label("skin_color")
    powers = sqlalchemy.func.array_agg(
        sqlalchemy.func.distinct(SuperheroModel.classes.superpower.power_name), type_=ARRAY(sqlalchemy.String)
    ).label("powers")
    attributes = sqlalchemy.func.jsonb_object_agg(
        SuperheroModel.classes.attribute.attribute_name, hero_attr.c.attribute_value
    ).label("attributes")


gender_similarity = SimilarityIndex(
    store=CaseInsensitiveSqlAlchemyStore(engine, "gender_similarity"),
    fetcher=SimpleSqlAlchemyFetcher(
        engine,
        table=SuperheroModel.classes.gender,
        column=SuperheroModel.classes.gender.gender,
    ),
)

# TODO: should be done periodically, not each time the file is initialized
gender_similarity.update()


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
        gender = gender_similarity.similar(gender)
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

    def __init__(self, sqlalchemy_engine: sqlalchemy.engine.Engine) -> None:
        self._inner = sqlalchemy.select()
        super().__init__(sqlalchemy_engine)

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return (
            sqlalchemy.select(
                SuperheroDBSchema.id,
                SuperheroDBSchema.name,
                SuperheroDBSchema.full_name,
                SuperheroDBSchema.gender,
                SuperheroDBSchema.race,
                SuperheroDBSchema.publisher_name,
                SuperheroDBSchema.alignment,
                SuperheroDBSchema.weight_kg,
                SuperheroDBSchema.height_cm,
                SuperheroDBSchema.eye_color,
                SuperheroDBSchema.hair_color,
                SuperheroDBSchema.skin_color,
                SuperheroDBSchema.powers,
                SuperheroDBSchema.attributes,
            )
            .join(
                SuperheroModel.classes.gender,
                SuperheroModel.classes.superhero.gender_id == SuperheroModel.classes.gender.id,
            )
            .join(
                SuperheroModel.classes.race, SuperheroModel.classes.superhero.race_id == SuperheroModel.classes.race.id
            )
            .join(
                SuperheroModel.classes.publisher,
                SuperheroModel.classes.superhero.publisher_id == SuperheroModel.classes.publisher.id,
            )
            .join(
                SuperheroModel.classes.alignment,
                SuperheroModel.classes.superhero.alignment_id == SuperheroModel.classes.alignment.id,
            )
            .join(eye_color_alias, SuperheroModel.classes.superhero.eye_colour_id == eye_color_alias.id)
            .join(hair_color_alias, SuperheroModel.classes.superhero.hair_colour_id == hair_color_alias.id)
            .join(skin_color_alias, SuperheroModel.classes.superhero.skin_colour_id == skin_color_alias.id)
            .join(hero_power, hero_power.c.hero_id == SuperheroModel.classes.superhero.id)
            .join(SuperheroModel.classes.superpower, SuperheroModel.classes.superpower.id == hero_power.c.power_id)
            .join(hero_attr, hero_attr.c.hero_id == SuperheroModel.classes.superhero.id)
            .join(SuperheroModel.classes.attribute, SuperheroModel.classes.attribute.id == hero_attr.c.attribute_id)
            .group_by(
                SuperheroDBSchema.id,
                SuperheroDBSchema.name,
                SuperheroDBSchema.full_name,
                SuperheroDBSchema.gender,
                SuperheroDBSchema.race,
                SuperheroDBSchema.publisher_name,
                SuperheroDBSchema.alignment,
                SuperheroDBSchema.weight_kg,
                SuperheroDBSchema.height_cm,
                SuperheroDBSchema.eye_color,
                SuperheroDBSchema.hair_color,
                SuperheroDBSchema.skin_color,
            )
        )

    @decorators.view_filter()
    def has_power(self, power: str) -> sqlalchemy.ColumnElement:
        return self._inner.c.powers.contains([power])

    #
    #
    # @decorators.view_filter()
    # def power_higher_than(self, power_level: int) -> sqlalchemy.ColumnElement:
    #     return self._inner.c.attributes["Power"] < power_level  # TODO: this does not work for some reason
    #
    #
    # @decorators.view_filter()
    # def combat_higher_than(self, combat_level: int) -> sqlalchemy.ColumnElement:
    #     return self._inner.c.attributes["Combat"] < combat_level  # TODO: this does not work for some reason

    @decorators.view_action()
    def sort_by_gender(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        return select.order_by(SuperheroModel.classes.superhero.gender_id)


# todo: sometimes I use classes, sometimes metadata.tables, because some classes aren't automapped correctly.
# at some point we should either fix the automap or use metadata.tables everywhere
class SuperheroCountByPowerView(SqlAlchemyBaseView, SuperheroFilterMixin):
    """
    View used to count the number of superheroes with a specific power.
    """

    def __init__(self, sqlalchemy_engine: sqlalchemy.engine.Engine) -> None:
        self._superhero_count = sqlalchemy.func.count(SuperheroModel.classes.superhero.id).label("superhero_count")
        self._hero_power = SuperheroModel.metadata.tables["hero_power"]

        super().__init__(sqlalchemy_engine)

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        # TODO: this should use part of the main query instead of replicating joins
        return (
            sqlalchemy.select(
                SuperheroModel.classes.superpower.power_name,
                self._superhero_count,
            )
            .join(self._hero_power, self._hero_power.c.hero_id == SuperheroModel.classes.superhero.id)
            .join(
                SuperheroModel.classes.superpower, SuperheroModel.classes.superpower.id == self._hero_power.c.power_id
            )
            .group_by(SuperheroModel.classes.superpower.power_name)
        )

    @decorators.view_filter()
    def filter_by_power(self, power: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superpower.power_name == power

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
    dbally.use_event_handler(CLIEventHandler())

    superheros_db = dbally.create_collection("superheros_db")
    superheros_db.add(SuperheroView, lambda: SuperheroView(engine))
    superheros_db.add(SuperheroCountByPowerView, lambda: SuperheroCountByPowerView(engine))

    await superheros_db.ask("What heroes have Blue eyes and are taller than 180.5cm?", return_natural_response=True)

    await superheros_db.ask("Count power of female heros", return_natural_response=True)


if __name__ == "__main__":
    asyncio.run(main())

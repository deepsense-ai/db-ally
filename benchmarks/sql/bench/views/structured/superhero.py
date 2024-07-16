# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import aliased

from dbally import SqlAlchemyBaseView, decorators

engine = create_engine("sqlite:///data/superhero.db")
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


class SuperheroFilterMixin:
    @decorators.view_filter()
    def filter_by_full_name(self, full_name: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.full_name == full_name

    @decorators.view_filter()
    def filter_by_superhero_name(self, name: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.superhero_name == name

    @decorators.view_filter()
    def filter_by_superhero_id(self, superhero_id: int) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.id == superhero_id

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
                SuperheroModel.classes.publisher.publisher_name == publisher
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
    def filter_by_power(self, power: str) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superpower.power_name == power

    @decorators.view_filter()
    def filter_by_missing_weight(self) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.weight_kg == 0 or SuperheroModel.classes.superhero.weight_kg is None

    @decorators.view_filter()
    def filter_by_weight(self, weight: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.weight_kg == weight

    @decorators.view_filter()
    def heavier_than(self, weight: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.weight_kg > weight

    @decorators.view_filter()
    def lighter_than(self, weight: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.weight_kg < weight

    @decorators.view_filter()
    def filter_by_height(self, height: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.height_cm == height

    @decorators.view_filter()
    def taller_than(self, height: float) -> sqlalchemy.ColumnElement:
        return SuperheroModel.classes.superhero.height_cm > height


class SuperheroView(SqlAlchemyBaseView, SuperheroFilterMixin):
    """
    Main view, meant for finding superheroes meeting specific criteria
    """

    def __init__(self, sqlalchemy_engine: sqlalchemy.engine.Engine) -> None:
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

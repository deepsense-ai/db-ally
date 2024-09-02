# pylint: disable=attribute-defined-outside-init, missing-docstring, missing-return-doc, missing-param-doc, singleton-comparison, consider-using-in, too-many-ancestors, too-many-public-methods
# flake8: noqa

from typing import Literal

from sqlalchemy import ColumnElement, Engine, Float, Select, case, cast, func, select
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import aliased, declarative_base

from dbally.views.decorators import view_aggregation, view_filter
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

Base = declarative_base(cls=DeferredReflection)


class Alignment(Base):
    __tablename__ = "alignment"


class Attribute(Base):
    __tablename__ = "attribute"


class Colour(Base):
    __tablename__ = "colour"


class Gender(Base):
    __tablename__ = "gender"


class HeroAttribute(Base):
    __tablename__ = "hero_attribute"
    __mapper_args__ = {"primary_key": ["hero_id", "attribute_id"]}


class HeroPower(Base):
    __tablename__ = "hero_power"
    __mapper_args__ = {"primary_key": ["hero_id", "power_id"]}


class Publisher(Base):
    __tablename__ = "publisher"


class Race(Base):
    __tablename__ = "race"


class Superhero(Base):
    __tablename__ = "superhero"


class Superpower(Base):
    __tablename__ = "superpower"


class DBInitMixin:
    def __init__(self, sqlalchemy_engine: Engine) -> None:
        """
        Initializes the view.

        Args:
            sqlalchemy_engine: The database engine.
        """
        DeferredReflection.prepare(sqlalchemy_engine)
        super().__init__(sqlalchemy_engine)


class SuperheroFilterMixin:
    """
    Mixin for filtering the view by the superhero attributes.
    """

    @view_filter()
    def filter_by_superhero_id(self, superhero_id: int) -> ColumnElement:
        """
        Filters the view by the superhero id.

        Args:
            superhero_id: The id of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.id == superhero_id

    @view_filter()
    def filter_by_superhero_name(self, superhero_name: str) -> ColumnElement:
        """
        Filters the view by the superhero nick or handle.

        Args:
            superhero_name: The abstract nick or handle of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.superhero_name == superhero_name

    @view_filter()
    def filter_by_missing_superhero_full_name(self) -> ColumnElement:
        """
        Filters the view by the missing full name of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.full_name == None

    @view_filter()
    def filter_by_superhero_full_name(self, superhero_full_name: str) -> ColumnElement:
        """
        Filters the view by the full name of the superhero.

        Args:
            superhero_full_name: The human name of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.full_name == superhero_full_name

    @view_filter()
    def filter_by_superhero_first_name(self, superhero_first_name: str) -> ColumnElement:
        """
        Filters the view by the simmilar full name of the superhero.

        Args:
            superhero_first_name: The first name of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.full_name.like(f"{superhero_first_name}%")

    @view_filter()
    def filter_by_height_cm(self, height_cm: float) -> ColumnElement:
        """
        Filters the view by the height of the superhero.

        Args:
            height_cm: The height of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.height_cm == height_cm

    @view_filter()
    def filter_by_height_cm_less_than(self, height_cm: float) -> ColumnElement:
        """
        Filters the view by the height of the superhero.

        Args:
            height_cm: The height of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.height_cm < height_cm

    @view_filter()
    def filter_by_height_cm_greater_than(self, height_cm: float) -> ColumnElement:
        """
        Filters the view by the height of the superhero.

        Args:
            height_cm: The height of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.height_cm > height_cm

    @view_filter()
    def filter_by_height_cm_between(self, begin_height_cm: float, end_height_cm: float) -> ColumnElement:
        """
        Filters the view by the height of the superhero.

        Args:
            begin_height_cm: The begin height of the superhero.
            end_height_cm: The end height of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.height_cm.between(begin_height_cm, end_height_cm)

    @view_filter()
    def filter_by_the_tallest(self) -> ColumnElement:
        """
        Filter the view by the tallest superhero.

        Returns:
            The filter condition.
        """
        return Superhero.height_cm == select(func.max(Superhero.height_cm)).scalar_subquery()

    @view_filter()
    def filter_by_missing_weight(self) -> ColumnElement:
        """
        Filters the view by the missing weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg == 0 or Superhero.weight_kg == None

    @view_filter()
    def filter_by_weight_kg(self, weight_kg: int) -> ColumnElement:
        """
        Filters the view by the weight of the superhero.

        Args:
            weight_kg: The weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg == weight_kg

    @view_filter()
    def filter_by_weight_kg_greater_than(self, weight_kg: int) -> ColumnElement:
        """
        Filters the view by the weight of the superhero.

        Args:
            weight_kg: The weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg > weight_kg

    @view_filter()
    def filter_by_weight_kg_less_than(self, weight_kg: int) -> ColumnElement:
        """
        Filters the view by the weight of the superhero.

        Args:
            weight_kg: The weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg < weight_kg

    @view_filter()
    def filter_by_weight_greater_than_percentage_of_average(self, average_percentage: int) -> ColumnElement:
        """
        Filters the view by the weight greater than the percentage of average of superheroes.

        Args:
            average_percentage: The percentage of the average weight.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg * 100 > select(func.avg(Superhero.weight_kg)).scalar_subquery() * average_percentage

    @view_filter()
    def filter_by_the_heaviest(self) -> ColumnElement:
        """
        Filters the view by the heaviest superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg == select(func.max(Superhero.weight_kg)).scalar_subquery()

    @view_filter()
    def filter_by_missing_publisher(self) -> ColumnElement:
        """
        Filters the view by the missing publisher of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.publisher_id == None


class SuperheroAggregationMixin:
    """
    Mixin for aggregating the view by the superhero attributes.
    """

    @view_aggregation()
    def count_superheroes(self) -> Select:
        """
        Counts the number of superheros.

        Returns:
            The superheros count.
        """
        return self.data.with_only_columns(func.count(Superhero.id).label("count_superheroes")).group_by(Superhero.id)

    @view_aggregation()
    def average_height(self) -> Select:
        """
        Averages the height of the superheros.

        Returns:
            The superheros average height.
        """
        return self.data.with_only_columns(func.avg(Superhero.height_cm).label("average_height")).group_by(Superhero.id)


class SuperheroColourFilterMixin:
    """
    Mixin for filtering the view by the superhero colour attributes.
    """

    @view_filter()
    def filter_by_eye_colour(self, eye_colour: str) -> ColumnElement:
        """
        Filters the view by the superhero eye colour.

        Args:
            eye_colour: The eye colour of the superhero.

        Returns:
            The filter condition.
        """
        return self.eye_colour.colour == eye_colour

    @view_filter()
    def filter_by_hair_colour(self, hair_colour: str) -> ColumnElement:
        """
        Filters the view by the superhero hair colour.

        Args:
            hair_colour: The hair colour of the superhero.

        Returns:
            The filter condition.
        """
        return self.hair_colour.colour == hair_colour

    @view_filter()
    def filter_by_skin_colour(self, skin_colour: str) -> ColumnElement:
        """
        Filters the view by the superhero skin colour.

        Args:
            skin_colour: The skin colour of the superhero.

        Returns:
            The filter condition.
        """
        return self.skin_colour.colour == skin_colour

    @view_filter()
    def filter_by_same_hair_and_eye_colour(self) -> ColumnElement:
        """
        Filters the view by the superhero with the same hair and eye colour.

        Returns:
            The filter condition.
        """
        return self.eye_colour.colour == self.hair_colour.colour

    @view_filter()
    def filter_by_same_hair_and_skin_colour(self) -> ColumnElement:
        """
        Filters the view by the superhero with the same hair and skin colour.

        Returns:
            The filter condition.
        """
        return self.hair_colour.colour == self.skin_colour.colour


class SuperheroColourAggregationMixin:
    """
    Mixin for aggregating the view by the superhero colour attributes.
    """

    @view_aggregation()
    def percentage_of_eye_colour(self, eye_colour: str) -> Select:
        """
        Calculates the percentage of objects with eye colour.

        Args:
            eye_colour: The eye colour of the object.

        Returns:
            The percentage of objects with eye colour.
        """
        return self.data.with_only_columns(
            (
                cast(func.count(case((self.eye_colour.colour == eye_colour, Superhero.id), else_=None)), Float)
                * 100
                / func.count(Superhero.id)
            ).label(f"percentage_of_{eye_colour.lower()}")
        )


class PublisherFilterMixin:
    """
    Mixin for filtering the view by the publisher attributes.
    """

    @view_filter()
    def filter_by_publisher_name(self, publisher_name: str) -> ColumnElement:
        """
        Filters the view by the publisher name.

        Args:
            publisher_name: The name of the publisher.

        Returns:
            The filter condition.
        """
        return Publisher.publisher_name == publisher_name


class PublisherAggregationMixin:
    """
    Mixin for aggregating the view by the publisher attributes.
    """

    @view_aggregation()
    def percentage_of_publisher(self, publisher_name: str) -> Select:
        """
        Calculates the percentage of objects with publisher.

        Args:
            publisher_name: The name of the publisher.

        Returns:
            The percentage of objects with publisher.
        """
        return self.data.with_only_columns(
            (
                cast(func.count(case((Publisher.publisher_name == publisher_name, Superhero.id), else_=None)), Float)
                * 100
                / func.count(Superhero.id)
            ).label(f"percentage_of_{publisher_name.lower()}")
        )


class AlignmentFilterMixin:
    """
    Mixin for filtering the view by the alignment attributes.
    """

    @view_filter()
    def filter_by_alignment(self, alignment: Literal["Good", "Bad", "Neutral", "N/A"]) -> ColumnElement:
        """
        Filters the view by the superhero alignment.

        Args:
            alignment: The alignment of the superhero.

        Returns:
            The filter condition.
        """
        return Alignment.alignment == alignment


class AlignmentAggregationMixin:
    """
    Mixin for aggregating the view by the alignment.
    """

    @view_aggregation()
    def percentage_of_alignment(self, alignment: Literal["Good", "Bad", "Neutral", "N/A"]) -> Select:
        """
        Calculates the percentage of objects with alignment.

        Args:
            alignment: The alignment of the object.

        Returns:
            The percentage of objects with alignment.
        """
        return self.data.with_only_columns(
            (
                cast(func.count(case((Alignment.alignment == alignment, Superhero.id), else_=None)), Float)
                * 100
                / func.count(Superhero.id)
            ).label(f"percentage_of_{alignment.lower()}")
        )


class GenderFilterMixin:
    """
    Mixin for filtering the view by the gender.
    """

    @view_filter()
    def filter_by_gender(self, gender: Literal["Male", "Female", "N/A"]) -> ColumnElement:
        """
        Filters the view by the object gender.

        Args:
            gender: The gender of the object.

        Returns:
            The filter condition.
        """
        return Gender.gender == gender


class GenderAggregationMixin:
    """
    Mixin for aggregating the view by the gender.
    """

    @view_aggregation()
    def percentage_of_gender(self, gender: Literal["Male", "Female", "N/A"]) -> Select:
        """
        Calculates the percentage of objects with gender.

        Args:
            gender: The gender of the object.

        Returns:
            The percentage of objects with gender.
        """
        return self.data.with_only_columns(
            (
                cast(func.count(case((Gender.gender == gender, Superhero.id), else_=None)), Float)
                * 100
                / func.count(Superhero.id)
            ).label(f"percentage_of_{gender.lower()}")
        )


class RaceFilterMixin:
    """
    Mixin for filtering the view by the race.
    """

    @view_filter()
    def filter_by_race(self, race: str) -> ColumnElement:
        """
        Filters the view by the object race.

        Args:
            race: The race of the object.

        Returns:
            The filter condition.
        """
        return Race.race == race


class SuperheroView(
    DBInitMixin,
    SqlAlchemyBaseView,
    SuperheroAggregationMixin,
    SuperheroFilterMixin,
    SuperheroColourFilterMixin,
    AlignmentAggregationMixin,
    AlignmentFilterMixin,
    GenderAggregationMixin,
    GenderFilterMixin,
    PublisherAggregationMixin,
    PublisherFilterMixin,
    RaceFilterMixin,
):
    """
    View for querying only superheros data. Contains the superhero id, superhero name, full name, height, weight,
    publisher name, gender, race, alignment, eye colour, hair colour, skin colour.
    """

    def get_select(self) -> Select:
        """
        Initializes the select object for the view.

        Returns:
            The select object.
        """
        self.eye_colour = aliased(Colour)
        self.hair_colour = aliased(Colour)
        self.skin_colour = aliased(Colour)

        return (
            select(
                Superhero.id,
                Superhero.superhero_name,
                Superhero.full_name,
                Superhero.height_cm,
                Superhero.weight_kg,
                Alignment.alignment,
                Gender.gender,
                Publisher.publisher_name,
                Race.race,
                self.eye_colour.colour.label("eye_colour"),
                self.hair_colour.colour.label("hair_colour"),
                self.skin_colour.colour.label("skin_colour"),
            )
            .join(Alignment, Alignment.id == Superhero.alignment_id)
            .join(Gender, Gender.id == Superhero.gender_id)
            .join(Publisher, Publisher.id == Superhero.publisher_id)
            .join(Race, Race.id == Superhero.race_id)
            .join(self.eye_colour, self.eye_colour.id == Superhero.eye_colour_id)
            .join(self.hair_colour, self.hair_colour.id == Superhero.hair_colour_id)
            .join(self.skin_colour, self.skin_colour.id == Superhero.skin_colour_id)
        )


class PublisherView(DBInitMixin, SqlAlchemyBaseView, PublisherFilterMixin):
    """
    View for querying only publisher data. Contains the publisher id and publisher name.
    """

    def get_select(self) -> Select:
        """
        Initializes the select object for the view.

        Returns:
            The select object.
        """
        return select(Publisher.id, Publisher.publisher_name)

# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc

from typing import Literal

from sqlalchemy import ColumnElement, Engine, Select, func, select
from sqlalchemy.ext.declarative import DeferredReflection, declarative_base
from sqlalchemy.orm import aliased

from dbally.views.decorators import view_filter
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
        return Superhero.full_name is None

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
    def filter_by_missing_weight(self) -> ColumnElement:
        """
        Filters the view by the missing weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg == 0 or Superhero.weight_kg is None

    @view_filter()
    def filter_by_weight_kg(self, weight_kg: float) -> ColumnElement:
        """
        Filters the view by the weight of the superhero.

        Args:
            weight_kg: The weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg == weight_kg

    @view_filter()
    def filter_by_weight_kg_bigger_than(self, weight_kg: float) -> ColumnElement:
        """
        Filters the view by the weight of the superhero.

        Args:
            weight_kg: The weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg > weight_kg

    @view_filter()
    def filter_by_weight_kg_lower_than(self, weight_kg: float) -> ColumnElement:
        """
        Filters the view by the weight of the superhero.

        Args:
            weight_kg: The weight of the superhero.

        Returns:
            The filter condition.
        """
        return Superhero.weight_kg < weight_kg


class SuperheroColourFilterMixin:
    """
    Mixin for filtering the view by the superhero colour attributes.
    """

    def __init__(self) -> None:
        super().__init__()
        self.eye_colour = aliased(Colour)
        self.hair_colour = aliased(Colour)
        self.skin_colour = aliased(Colour)

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


class SuperpowerFilterMixin:
    """
    Mixin for filtering the view by the superpower attributes.
    """

    @view_filter()
    def filter_by_power_name(self, power_name: str) -> ColumnElement:
        """
        Filters the view by the superpower name.

        Args:
            power_name: The name of the superpower.

        Returns:
            The filter condition.
        """
        return Superpower.power_name == power_name


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


class HeroAttributeFilterMixin:
    """
    Mixin for filtering the view by the hero attribute.
    """

    @view_filter()
    def filter_by_attribute_value(self, attribute_value: int) -> ColumnElement:
        """
        Filters the view by the hero attribute value.

        Args:
            attribute_value: The value of the hero attribute.

        Returns:
            The filter condition.
        """
        return HeroAttribute.attribute_value == attribute_value

    @view_filter()
    def filter_by_attribute_value_between(self, begin_attribute_value: int, end_attribute_value: int) -> ColumnElement:
        """
        Filters the view by the hero attribute value.

        Args:
            begin_attribute_value: The begin value of the hero attribute.
            end_attribute_value: The end value of the hero attribute.

        Returns:
            The filter condition.
        """
        return HeroAttribute.attribute_value.between(begin_attribute_value, end_attribute_value)

    @view_filter()
    def filter_by_the_lowest_attribute_value(self) -> ColumnElement:
        """
        Filters the view by the lowest hero attribute value.

        Returns:
            The filter condition.
        """
        return HeroAttribute.attribute_value == select(func.min(HeroAttribute.attribute_value)).scalar_subquery()


class AttributeFilterMixin:
    """
    Mixin for filtering the view by the attribute.
    """

    @view_filter()
    def filter_by_attribute_name(
        self, attribute_name: Literal["Intelligence", "Strength", "Speed", "Durability", "Power", "Combat"]
    ) -> ColumnElement:
        """
        Filters the view by the attribute name.

        Args:
            attribute_name: The name of the attribute.

        Returns:
            The filter condition.
        """
        return Attribute.attribute_name == attribute_name


class SuperheroView(  # pylint: disable=too-many-ancestors
    DBInitMixin,
    SqlAlchemyBaseView,
    SuperheroFilterMixin,
    SuperheroColourFilterMixin,
    PublisherFilterMixin,
    AlignmentFilterMixin,
    GenderFilterMixin,
    RaceFilterMixin,
    HeroAttributeFilterMixin,
):
    """
    View containing superhero data for querying superheroes.
    """

    def get_select(self) -> Select:
        """
        Initializes the select object for the view.

        Returns:
            The select object.
        """
        return (
            select(
                Superhero.id,
                Superhero.superhero_name,
                Superhero.full_name,
                Superhero.height_cm,
                Superhero.weight_kg,
                Publisher.publisher_name,
                Gender.gender,
                Race.race,
                Alignment.alignment,
                self.eye_colour.colour.label("eye_colour"),
                self.hair_colour.colour.label("hair_colour"),
                self.skin_colour.colour.label("skin_colour"),
            )
            .join(Publisher, Publisher.id == Superhero.publisher_id)
            .join(Race, Race.id == Superhero.race_id)
            .join(Gender, Gender.id == Superhero.gender_id)
            .join(Alignment, Alignment.id == Superhero.alignment_id)
            .join(self.eye_colour, self.eye_colour.id == Superhero.eye_colour_id)
            .join(self.hair_colour, self.hair_colour.id == Superhero.hair_colour_id)
            .join(self.skin_colour, self.skin_colour.id == Superhero.skin_colour_id)
            .join(HeroAttribute, HeroAttribute.hero_id == Superhero.id)
        )


class HeroAttributeView(DBInitMixin, SqlAlchemyBaseView, HeroAttributeFilterMixin, AttributeFilterMixin):
    """
    View containing hero attribute data for querying superhero attributes.
    """

    def get_select(self) -> Select:
        """
        Initializes the select object for the view.

        Returns:
            The select object.
        """
        return select(
            HeroAttribute.hero_id,
            Attribute.attribute_name,
            HeroAttribute.attribute_value,
        ).join(Attribute, Attribute.id == HeroAttribute.attribute_id)


class HeroPowerView(DBInitMixin, SqlAlchemyBaseView, SuperheroFilterMixin, SuperpowerFilterMixin):
    """
    View containing hero superpowers data for querying hero superpowers.
    """

    def get_select(self) -> Select:
        """
        Initializes the select object for the view.

        Returns:
            The select object.
        """
        return (
            select(
                HeroPower.hero_id,
                Superhero.superhero_name,
                Superpower.power_name,
            )
            .join(Superhero, Superhero.id == HeroPower.hero_id)
            .join(Superpower, Superpower.id == HeroPower.power_id)
        )


class PublisherView(DBInitMixin, SqlAlchemyBaseView, PublisherFilterMixin):
    """
    View containing publisher data for querying publishers.
    """

    def get_select(self) -> Select:
        """
        Initializes the select object for the view.

        Returns:
            The select object.
        """
        return select(Publisher.id, Publisher.publisher_name)

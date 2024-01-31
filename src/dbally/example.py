# pylint: disable=missing-docstring, missing-return-doc, missing-param-doc

import sqlalchemy
from sqlalchemy import orm

from dbally import Runner, SqlAlchemyBaseView, decorators, default_registry


class Base(orm.DeclarativeBase):
    """
    Base class for SQLAlchemy models
    """


class ExampleDbModel(Base):
    """
    SQLAlchemy model used as an example
    """

    __tablename__ = "example"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    dog_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)


@decorators.view()
class HelloView(SqlAlchemyBaseView):
    """
    View used as an example
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return sqlalchemy.select(ExampleDbModel)

    @decorators.view_filter()
    def filter_by_id(self, idx: int) -> sqlalchemy.ColumnElement:
        """
        Filter by id
        """
        return ExampleDbModel.id == idx

    @decorators.view_filter()
    def filter_by_city(self, city: str) -> sqlalchemy.ColumnElement:
        return ExampleDbModel.city == city

    @decorators.view_filter()
    def filter_by_dog(self, name: str) -> sqlalchemy.ColumnElement:
        """
        Filter by dog name
        """
        return ExampleDbModel.dog_name == name

    @decorators.view_filter()
    def filter_by_is_gentelman(self) -> sqlalchemy.ColumnElement:
        """
        Only show people who are proper gentlemen
        """
        return (ExampleDbModel.name == "John") | (ExampleDbModel.city == "London")

    @decorators.view_action()
    def sort_by_city(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        return select.order_by(ExampleDbModel.city)

    @decorators.view_action()
    def group_by_city(self, select: sqlalchemy.Select) -> sqlalchemy.Select:
        return select.group_by(ExampleDbModel.city)


if __name__ == "__main__":
    # TODO: Replace the example with automated tests and documentation

    print("Available views:")
    print(default_registry.list())
    print()

    print("HelloView details:")
    view = default_registry.get("HelloView")
    print()

    print("Filters:")
    print("\n".join([str(f) for f in view.list_filters()]))
    print()

    print("Actions:")
    print("\n".join([str(a) for a in view.list_actions()]))
    print()

    print("SQL:")
    r = Runner("HelloView")
    r.apply_filters("(filter_by_id(1) or filter_by_is_gentelman()) and filter_by_dog('Rex')")
    r.apply_actions("sort_by_city()\ngroup_by_city()")

    print(r.generate_sql())

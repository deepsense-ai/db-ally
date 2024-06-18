import sqlalchemy
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base

from dbally import SqlAlchemyBaseView
from dbally.views import decorators

engine2 = create_engine("postgresql+pg8000://postgres:ikar89pl@localhost:5432/codebase_community")

Base2 = automap_base()
Base2.prepare(autoload_with=engine2)
CommunityUsers = Base2.classes.users


class CommunityUsersView(SqlAlchemyBaseView):
    """
    A view for retrieving community users from the database.
    """

    def get_select(self) -> sqlalchemy.Select:
        """
        Creates the initial SqlAlchemy select object, which will be used to build the query.
        """
        return sqlalchemy.select(CommunityUsers)

    @decorators.view_filter()
    def most_popular_views(self, years: int) -> sqlalchemy.ColumnElement:
        """
        Filters users with a lot of `views` .
        """
        return CommunityUsers.views >= years

    @decorators.view_filter()
    def good_reputation(self) -> sqlalchemy.ColumnElement:
        """
        Filters users with `reputation` high reputation.
        """
        return CommunityUsers.reputation >= 1000


# def main():
#     from sqlalchemy import create_engine
#
#     df = pd.read_sql_table("users", engine.connect())
#     print(df)
#
#
# if __name__ == "__main__":
#     main()

import pandas as pd
from sqlalchemy import create_engine, inspect


def main():
    engine = create_engine(r"sqlite:////home/karllu/projects/db-ally/candidates.db")
    insp = inspect(engine)
    print(insp.get_table_names())
    pd.read_sql_table(insp.get_table_names()[0], engine)


if __name__ == "__main__":
    main()

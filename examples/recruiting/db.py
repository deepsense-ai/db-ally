import csv
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

ENGINE = create_engine("sqlite://")
CSV_PATH = Path(__file__).parent / "data"


class Base(DeclarativeBase):
    """
    This class represents the base of the recruitment database.
    """


class Candidate(Base):
    """
    This class represents the candidate table in the recruitment database.
    """

    __tablename__ = "candidate"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    country: Mapped[str]
    years_of_experience: Mapped[int]
    position: Mapped[str]
    university: Mapped[str]
    skills: Mapped[str]
    tags: Mapped[str]
    available_from: Mapped[str]

    def __repr__(self) -> str:
        return f"Candidate(id={self.id!r}, name={self.name!r}, country={self.country!r},\
            years_of_experience={self.years_of_experience!r}, position={self.position!r},\
            university={self.university!r}), skills={self.skills!r}, tags={self.tags!r}),\
            available_from={self.available_from!r})"


class JobOffer(Base):
    """
    This class represents the offer table in the recruitment database.
    """

    __tablename__ = "offer"
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str]
    position: Mapped[str]
    excpected_years_of_experience: Mapped[int]
    salary: Mapped[str]

    def __repr__(self) -> str:
        return f"Offer(id={self.id!r}, company={self.company!r},\
            position={self.position!r}, excpected_years_of_experience={self.excpected_years_of_experience!r},\
            salary={self.salary!r})"


class Application(Base):
    """
    This class represents the application table in the recruitment database.
    """

    __tablename__ = "application"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int]
    job_offer_id: Mapped[str]
    status: Mapped[str]

    def __repr__(self) -> str:
        return f"Application(id={self.id!r}, candidate_id={self.candidate_id!r}, job_offer_id={self.job_offer_id!r},\
            status={self.status!r})"


Base.metadata.create_all(ENGINE)


def fill_candidate_table() -> None:
    """
    Fills the candidate table with data from the dbally/examples/recruiting.csv file.
    """
    with Session(ENGINE) as session:
        candidates = []
        with open(CSV_PATH / "recruiting.csv", newline="", encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                candidate = Candidate(
                    id=i,
                    name=row["name"],
                    country=row["country"],
                    years_of_experience=row["years_of_experience"],
                    position=row["position"],
                    university=row["university"],
                    skills=row["skills"],
                    tags=row["tags"],
                    available_from=row["available_from"],
                )
                candidates.append(candidate)

        session.add_all(candidates)
        session.commit()

        offers = []
        with open(CSV_PATH / "offers.csv", newline="", encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                offer = JobOffer(
                    company=row["company"],
                    position=row["position"],
                    excpected_years_of_experience=row["expected_years_of_experience"],
                    salary=row["salary"],
                )
                offers.append(offer)

        session.add_all(offers)
        session.commit()

        applications = []
        with open(CSV_PATH / "application.csv", newline="", encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                application = Application(
                    candidate_id=row["candidate_id"],
                    job_offer_id=row["job_offer_id"],
                    status=row["status"],
                )
                applications.append(application)

        session.add_all(applications)
        session.commit()


def get_recruitment_db_description(descriptions: Optional[Dict[str, str]] = None) -> str:
    """Generates a description of the recruitment database.

    Args:
        descriptions (Dict[str, str]): A dictionary with column names as keys and their descriptions as values.

    Returns:
        str: A description of the recruitment database.
    """
    if descriptions is None:
        descriptions = {
            "id": "Unique identifier of the candidate",
            "name": "Name of the candidate",
            "country": "Country of the candidate",
            "years_of_experience": "Years of experience of the candidate",
            "position": "Position of the candidate",
            "university": "University of the candidate",
        }

    metadata = MetaData()
    metadata.reflect(bind=ENGINE)

    db_description = ""
    for table in metadata.tables.values():
        db_description += f"Table: {table.name}\n"
        for column in table.c:
            db_description += f"  {column.name}[{column.type}]: {descriptions.get(column.name, 'No description')}\n"

    return db_description

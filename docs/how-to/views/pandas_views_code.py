# pylint: disable=missing-return-doc, missing-param-doc, missing-function-docstring, missing-class-docstring, missing-raises-doc
import dbally
import asyncio
import pandas as pd

from dbally import decorators, DataFrameBaseView
from dbally.audit.event_handlers.cli_event_handler import CLIEventHandler
from dbally.llms.clients.litellm import LiteLLM


class CandidateView(DataFrameBaseView):
    """
    View for retrieving information about candidates.
    """
    @decorators.view_filter()
    def at_least_experience(self, years: int) -> pd.Series:
        """
        Filters candidates with at least `years` of experience.
        """
        return self.df.years_of_experience >= years

    @decorators.view_filter()
    def from_country(self, country: str) -> pd.Series:
        """
        Filters candidates from a specific country.
        """
        return self.df.country == country

    @decorators.view_filter()
    def senior_data_scientist_position(self) -> pd.Series:
        """
        Filters candidates that can be considered for a senior data scientist position.
        """
        return self.df.position.isin(["Data Scientist", "Machine Learning Engineer", "Data Engineer"]) \
            & (self.df.years_of_experience >= 3)

CANDIDATE_DATA = pd.DataFrame.from_records([
    {"id": 1, "name": "John Doe", "position": "Data Scientist", "years_of_experience": 2, "country": "France"},
    {"id": 2, "name": "Jane Doe", "position": "Data Engineer", "years_of_experience": 3, "country": "France"},
    {"id": 3, "name": "Alice Smith", "position": "Machine Learning Engineer", "years_of_experience": 4, "country": "Germany"},
    {"id": 4, "name": "Bob Smith", "position": "Data Scientist", "years_of_experience": 5, "country": "Germany"},
    {"id": 5, "name": "Janka Jankowska", "position": "Data Scientist", "years_of_experience": 3, "country": "Poland"},
])

async def main():
    llm = LiteLLM(model_name="gpt-3.5-turbo")
    collection = dbally.create_collection("recruitment", llm, event_handlers=[CLIEventHandler()])
    collection.add(CandidateView, lambda: CandidateView(CANDIDATE_DATA))

    result = await collection.ask("Find me French candidates suitable for a senior data scientist position.")

    print(f"Retrieved {len(result.results)} candidates:")
    for candidate in result.results:
        print(candidate)


if __name__ == "__main__":
    asyncio.run(main())

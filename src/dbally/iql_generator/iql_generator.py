from dbally.iql_generator.iql_aggregation_generator import IQLAggregationGenerator
from dbally.iql_generator.iql_filters_generator import IQLFiltersGenerator


class IQLGenerator:
    """
    Container class for IQL related operations such as filters or aggregation generation.
    """

    def __init__(self, filters_generator: IQLFiltersGenerator, aggregation_generator: IQLAggregationGenerator) -> None:
        """
        Constructs a new IQLGenerator instance.

        Args:
            filters_generator: Filters generator used to generate IQL filters
            aggregation_generator: Aggregation generator used to generate IQL aggregation
        """
        self._filters_generator = filters_generator
        self._aggregation_generator = aggregation_generator

    @property
    def filters(self) -> IQLFiltersGenerator:
        """
        Returns:
            Filters generator used to generate IQL filters
        """
        return self._filters_generator

    @property
    def aggregation(self) -> IQLAggregationGenerator:
        """
        Returns:
            Aggregation generator used to generate IQL aggregation
        """
        return self._aggregation_generator

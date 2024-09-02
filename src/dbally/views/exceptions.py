from dbally.exceptions import DbAllyError
from dbally.iql_generator.iql_generator import IQLGeneratorState


class ViewExecutionError(DbAllyError):
    """
    Exception for when an error occurs while executing a view.
    """

    def __init__(
        self,
        view_name: str,
        iql: IQLGeneratorState,
    ) -> None:
        """
        Args:
            view_name: Name of the view that caused the error.
            iql: View IQL generator state.
        """
        super().__init__(f"Error while executing view {view_name}")
        self.view_name = view_name
        self.iql = iql

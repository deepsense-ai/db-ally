class ContextNotAvailableError(Exception):
    """
    An exception inheriting from BaseContextException pointining that no sufficient context information
    was provided by the user while calling view.ask().
    """

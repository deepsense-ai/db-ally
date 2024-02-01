from ._collection import DBAllyCollection


def create_collection(name: str) -> DBAllyCollection:
    """
    Create a new collection that is a container for registering views, configuration and main entrypoint to db-ally
    features.

    Args:
         name: The name of the collection

    Returns:
        a new instance of DBAllyCollection
    """
    return DBAllyCollection(name)

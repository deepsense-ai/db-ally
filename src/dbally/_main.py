from ._collection import Collection


def create_collection(name: str) -> Collection:
    """
    Create a new collection that is a container for registering views, configuration and main entrypoint to db-ally
    features.

    Args:
         name: The name of the collection

    Returns:
        a new instance of DBAllyCollection
    """
    return Collection(name)

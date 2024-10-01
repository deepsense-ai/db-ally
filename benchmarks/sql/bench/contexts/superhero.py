from dataclasses import dataclass

from dbally.context import Context


@dataclass
class UserContext(Context):
    """
    Current user data.
    """

    name: str = "John Doe"


@dataclass
class SuperheroContext(Context):
    """
    Current user favourite superhero data.
    """

    name: str = "Batman"

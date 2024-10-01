from typing import Dict, Type

from dbally.context import Context

from .superhero import SuperheroContext, UserContext

CONTEXTS_REGISTRY: Dict[str, Type[Context]] = {
    UserContext.__name__: UserContext,
    SuperheroContext.__name__: SuperheroContext,
}

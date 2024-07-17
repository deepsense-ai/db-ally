from typing import Dict, Type

from dbally.views.base import BaseView

from .freeform.superhero import SuperheroFreeformView
from .structured.superhero import SuperheroView

VIEWS_REGISTRY: Dict[str, Type[BaseView]] = {
    SuperheroView.__name__: SuperheroView,
    SuperheroFreeformView.__name__: SuperheroFreeformView,
}

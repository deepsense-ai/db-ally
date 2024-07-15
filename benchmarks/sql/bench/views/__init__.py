from typing import Dict, Type

from dbally.views.base import BaseView

from .freeform.superhero import SuperheroFreeformView
from .structured.superhero import SuperheroView

STRUCTURED_VIEWS_REGISTRY: Dict[str, Type[BaseView]] = {
    SuperheroView.__name__: SuperheroView,
}

FREEFORM_VIEWS_REGISTRY: Dict[str, Type[BaseView]] = {
    SuperheroFreeformView.__name__: SuperheroFreeformView,
}

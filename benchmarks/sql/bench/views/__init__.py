from typing import Dict, Type

from dbally.views.base import BaseView

from .freeform.superhero import SuperheroFreeformView
from .structured.superhero import PublisherView, SuperheroView

VIEWS_REGISTRY: Dict[str, Type[BaseView]] = {
    PublisherView.__name__: PublisherView,
    SuperheroView.__name__: SuperheroView,
    SuperheroFreeformView.__name__: SuperheroFreeformView,
}

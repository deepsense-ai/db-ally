from typing import Dict, Type

from dbally.views.base import BaseView

from .freeform.superhero import SuperheroFreeformView
from .structured.superhero import HeroAttributeView, HeroPowerView, PublisherView, SuperheroView

VIEWS_REGISTRY: Dict[str, Type[BaseView]] = {
    PublisherView.__name__: PublisherView,
    HeroAttributeView.__name__: HeroAttributeView,
    HeroPowerView.__name__: HeroPowerView,
    SuperheroView.__name__: SuperheroView,
    SuperheroFreeformView.__name__: SuperheroFreeformView,
}

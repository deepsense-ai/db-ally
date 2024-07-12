from typing import Dict, Type

from dbally.views.freeform.text2sql.view import BaseText2SQLView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from .freeform.superhero import SuperheroFreeformView
from .structured.superhero import SuperheroView

STRUCTURED_VIEW_REGISTRY: Dict[str, Type[SqlAlchemyBaseView]] = {
    SuperheroView.__name__: SuperheroView,
}

FREEFORM_VIEW_REGISTRY: Dict[str, Type[BaseText2SQLView]] = {
    SuperheroFreeformView.__name__: SuperheroFreeformView,
}

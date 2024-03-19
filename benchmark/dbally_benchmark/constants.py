from enum import Enum
from typing import Dict, Type

from dbally_benchmark.views.superhero import SuperheroCountByPowerView, SuperheroView

from dbally.views.sqlalchemy_base import SqlAlchemyBaseView


class ViewName(Enum):
    """Enum representing the name of the view."""

    SUPERHERO_VIEW = "SuperheroView"
    SUPERHERO_COUNT_BY_POWER_VIEW = "SuperheroCountByPowerView"


class EvaluationType(Enum):
    """Enum representing the type of evaluation."""

    END2END = "e2e"
    TEXT2SQL = "text2sql"
    IQL = "iql"


VIEW_REGISTRY: Dict[ViewName, Type[SqlAlchemyBaseView]] = {
    ViewName.SUPERHERO_VIEW: SuperheroView,
    ViewName.SUPERHERO_COUNT_BY_POWER_VIEW: SuperheroCountByPowerView,
}

# Import all the models, so that Base has them before being
# imported by Alembic

from mspt.settings.database import DBModel  #noqa
from mspt.apps.users.models import User  #noqa
from mspt.apps.mspt.models import (
    Instrument,
    Style,
    StrategyImage,
    Strategy,
    TradeImage,
    Trade,
)  #noqa
from mspt.apps.cot.models import (
    CFTCContract,
    CFTCReport,
)  #noqa



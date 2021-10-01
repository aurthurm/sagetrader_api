import logging, coloredlogs

from mspt.apps.users import models as user_models
from mspt.settings import config
from mspt.apps.mspt import schemas, models, crud


coloredlogs.install()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

trading_styles = [
    schemas.StyleCreate(name="Scalp Trade", description="", owner_uid=None, public=False),
    schemas.StyleCreate(name="Day Trade", description="", owner_uid=None, public=False),
    schemas.StyleCreate(name="Short Term Trade", description="", owner_uid=None, public=False),
    schemas.StyleCreate(name="Swing Trade", description="", owner_uid=None, public=False),
    schemas.StyleCreate(name="Position Trade", description="", owner_uid=None, public=False),
]


def initialise_styles(db_session):
    logger.info("Initializing Trading Styles")
    for style_in in trading_styles: 
        style = crud.style.get_by_name(db_session, name=style_in.name)
        if not style:
            crud.style.create(db_session, obj_in=style_in)
        else:
            logger.info(f"Trading Styles exists {style.name}")
    logger.info("Trading Styles Initialised")
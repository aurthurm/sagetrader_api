import logging, coloredlogs
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from mspt.settings.database import db_session
from .admin import create_super_user
from .mspt import initialise_styles
from .cot import initialise_cot

coloredlogs.install()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_mspt():
    logger.info("Initializing MSPT")
    
    db_status()
    create_super_user(db_session)
    initialise_styles(db_session)
    initialise_cot(db_session)
    
    logger.info("MSPT Initializing Success :) YaY")
    return True


max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def db_status():
    logger.info("Checking database status")
    
    try:
        # Try to create session to check if DB is awake
        db_session.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e
    
    logger.info("Database connect established: PASS")
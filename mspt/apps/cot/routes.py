import logging, coloredlogs

from typing import List
import time
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Form,
    Query,
)
from sqlalchemy.orm import Session

from mspt.apps.cot import (
    schemas,
    models,
    crud,
    utils
)
from mspt.apps.users import models as user_models
from mspt.settings.database import get_db

coloredlogs.install()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()
db_session = Session()


@router.get("/fetch-cot-contracts", response_model=List[schemas.CFTCContract])
def fetch_cot_contracts(
    *,
    db: Session = Depends(get_db),
):
    contracts = crud.ctfc_contract.get_multi(db_session=db)
    return contracts


@router.get("/fetch-cot-reports/{contract_name}", response_model=List[schemas.CFTCReport])
def fetch_cot_reports(
    *,
    db: Session = Depends(get_db),
    contract_name: str,
):
    contract = crud.ctfc_contract.get_by_name(db_session=db, name=contract_name)
    reports = crud.cftc_report.get_reports_for_contract(db_session=db, contract_uid=contract.uid)
    return reports


@router.get("/fetch-cot-pair-biases")
def fetch_cot_pair_biases(
    *,
    db: Session = Depends(get_db),
):
    reports = utils.forex_pair_biases(db_session=db)
    return reports


@router.get("/refresh-cot-data")
async def refresh_cot_data(
    *,
    db: Session = Depends(get_db),
):
    logger.info("Loading cot data from quandl")
    db_cntrcts = crud.ctfc_contract.get_multi(db_session=db)
    logger.info(f"Contracts to execute {db_cntrcts}")
    for ctr in db_cntrcts:
        logger.info(f"Fetching {ctr.name} Contract data from quandl ")
        data_all, data_ch = utils.get_data(ctr.code)
        logger.info(f"persisiting ...")
        utils.persist_data(db, ctr, data_all, data_ch)
    return True


@router.get("/refresh-cot-data-test")
async def refresh_cot_data_test(
    *,
    db: Session = Depends(get_db),
):
    logger.info("Loading cot data from quandl")
    db_cntrcts = crud.ctfc_contract.get_multi(db_session=db)
    logger.info(f"Contracts to execute {db_cntrcts}")
    for ctr in db_cntrcts:
        if ctr.name in ["USDX", "GBP", "EUR"]:
            logger.info(f"Fetching {ctr.name} Contract data from quandl ")
            data_all, data_ch = utils.get_data(ctr.code)
            logger.info(f"persisiting ...")
            utils.persist_data(db, ctr, data_all, data_ch)
    return True

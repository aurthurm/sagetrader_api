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

router = APIRouter()
db_session = Session()


@router.get("/fetch-cot-contracts", response_model=List[schemas.CFTCContract])
def fetch_files(
    *,
    db: Session = Depends(get_db),
):
    contracts = crud.ctfc_contract.get_multi(db_session=db)
    return contracts


@router.get("/fetch-cot-reports/{contract_name}", response_model=List[schemas.CFTCReport])
def fetch_files(
    *,
    db: Session = Depends(get_db),
    contract_name: str,
):
    contract = crud.ctfc_contract.get_by_name(db_session=db, name=contract_name)
    reports = crud.cftc_report.get_reports_for_contract(db_session=db, contract_uid=contract.uid)
    return reports


@router.get("/fetch-cot-pair-biases")
def fetch_files(
    *,
    db: Session = Depends(get_db),
):
    reports = utils.forex_pair_biases(db_session=db)
    return reports

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.encoders import jsonable_encoder

from mspt.apps.cot import models
from mspt.apps.cot import schemas
from mspt.apps.mixins.crud import CRUDMIXIN


class CRUDCFTCContract(CRUDMIXIN[models.CFTCContract, schemas.CFTCContractCreate, schemas.CFTCContractUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[models.CFTCContract]:
        result = db_session.query(models.CFTCContract).filter(models.CFTCContract.name.ilike(name)).first()
        return result


class CRUDCFTCReport(CRUDMIXIN[models.CFTCReport, schemas.CFTCReportCreate, schemas.CFTCReportUpdate]):
    def get_report(self, db_session: Session, *, date: str, contract_uid: int) -> Optional[models.CFTCReport]:
        result = db_session.query(models.CFTCReport).filter(models.CFTCReport.date == date, models.CFTCReport.contract_uid == contract_uid).first()
        return result
    
    def get_by_date(self, db_session: Session, *, date: str) -> Optional[models.CFTCReport]:
        results = db_session.query(models.CFTCReport).filter(models.CFTCReport.date == date).all()
        return results

    def get_multi(self, db_session: Session, *, skip=0, limit=100) -> Optional[models.CFTCReport]:
        return db_session.query(self.model).order_by(self.model.date.desc()).offset(skip).limit(limit).all()
    
    def get_reports_for_contract(self, db_session: Session, *, contract_uid: int, skip=0, limit=25) -> Optional[List[models.CFTCReport]]:
        results = db_session.query(self.model).filter(self.model.contract_uid == contract_uid).order_by(self.model.date.desc()).offset(skip).limit(limit).all()
        return results 


ctfc_contract = CRUDCFTCContract(models.CFTCContract)
cftc_report = CRUDCFTCReport(models.CFTCReport)

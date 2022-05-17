from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from mspt.apps.mspt import models
from mspt.apps.mspt import schemas
from mspt.settings.security import verify_password, get_password_hash
from mspt.apps.mixins.crud import CRUDMIXIN


class CRUDInstrument(CRUDMIXIN[models.Instrument, schemas.InstrumentCreate, schemas.InstrumentUpdate]):
    def get_by_name_owner(self, db_session: Session, *, name: str, owner_uid: int) -> Optional[models.Instrument]:
        name = name.upper()
        result = db_session.query(models.Instrument).filter(models.Instrument.name == name,
                                                            models.Instrument.owner_uid == owner_uid).first()
        return result


instrument = CRUDInstrument(models.Instrument)


class CRUDStyle(CRUDMIXIN[models.Style, schemas.StyleCreate, schemas.StyleUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[models.Style]:
        result = db_session.query(models.Style).filter(models.Style.name == name).first()
        return result


style = CRUDStyle(models.Style)


class CRUDStrategy(CRUDMIXIN[models.Strategy, schemas.StrategyCreate, schemas.StrategyUpdate]):
    def get_by_name_owner(self, db_session: Session, *, name: str, owner_uid: int) -> Optional[models.Strategy]:
        result = db_session.query(models.Strategy).filter(models.Strategy.name == name,
                                                          models.Strategy.owner_uid == owner_uid).first()
        return result


strategy = CRUDStrategy(models.Strategy)


class CRUDTrade(CRUDMIXIN[models.Trade, schemas.TradeCreate, schemas.TradeUpdate]):
    def create(self, db_session: Session, *, obj_in: schemas.TradeCreate) -> models.Trade:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        # parse uid's as integers
        db_obj.instrument_uid = int(db_obj.instrument_uid)
        db_obj.strategy_uid = int(db_obj.strategy_uid)
        db_obj.style_uid = int(db_obj.style_uid)
        # relationship mode linkages
        db_obj.instrument = db_session.query(models.Instrument).get(db_obj.instrument_uid)
        db_obj.strategy = db_session.query(models.Strategy).get(db_obj.strategy_uid)
        db_obj.style = db_session.query(models.Style).get(db_obj.style_uid)
        ###
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def update(
        self, db_session: Session, *, db_obj: models.Trade, obj_in: schemas.TradeUpdate
    ) -> models.Trade:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        # reset relationship mode linkages
        obj_in_data = jsonable_encoder(obj_in)
        db_obj.instrument = db_session.query(models.Instrument).get(obj_in_data["instrument_uid"])
        db_obj.strategy = db_session.query(models.Strategy).get(obj_in_data["strategy_uid"])
        db_obj.style = db_session.query(models.Style).get(obj_in_data["style_uid"])
        ##
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj


trade = CRUDTrade(models.Trade)


class CRUDTradingPlan(CRUDMIXIN[models.TradingPlan, schemas.TradingPlanCreate, schemas.TradingPlanUpdate]):
    def get_by_name_owner(self, db_session: Session, *, name: str, owner_uid: int) -> Optional[models.TradingPlan]:
        result = db_session.query(models.TradingPlan).filter(models.TradingPlan.name == name,
                                                             models.TradingPlan.owner_uid == owner_uid).first()
        return result


trading_plan = CRUDTradingPlan(models.TradingPlan)


class CRUDTask(CRUDMIXIN[models.Task, schemas.TaskCreate, schemas.TaskUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[models.Task]:
        result = db_session.query(models.Task).filter(models.Task.name == name).first()
        return result


task = CRUDTask(models.Task)


class CRUDStudy(CRUDMIXIN[models.Study, schemas.StudyCreate, schemas.StudyUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[models.Study]:
        result = db_session.query(models.Study).filter(models.Study.name == name).first()
        return result


study = CRUDStudy(models.Study)


class CRUDStudyItem(CRUDMIXIN[models.StudyItem, schemas.StudyItemCreate, schemas.StudyItemUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[models.StudyItem]:
        result = db_session.query(models.StudyItem).filter(models.StudyItem.name == name).first()
        return result

    def get_multi_by_study(self, db_session: Session, *, study_uid: int, skip=0, limit=100) -> List[models.StudyItem]:
        return db_session.query(self.model).filter(models.StudyItem.study_uid == study_uid).offset(skip).limit(
            limit).all()

    def create(self, db_session: Session, *, obj_in: schemas.StudyItemCreateWithAttrs) -> models.StudyItem:
        obj_in_data = jsonable_encoder(obj_in)
        attrs = obj_in_data['attributes']
        del obj_in_data['attributes']
        db_obj = self.model(**obj_in_data)
        # parse uid's as integers
        db_obj.instrument_uid = int(db_obj.instrument_uid)
        db_obj.style_uid = int(db_obj.style_uid)
        # relationship mode linkages
        db_obj.instrument = db_session.query(models.Instrument).get(db_obj.instrument_uid)
        db_obj.style = db_session.query(models.Style).get(db_obj.style_uid)
        ###
        for _attr in attrs:
            attr = db_session.query(models.Attribute).get(_attr["uid"])
            if not attr in db_obj.attributes:
                db_obj.attributes.append(attr)
        ###
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def update(self, db_session: Session, *, db_obj: models.StudyItem,
               obj_in: schemas.StudyItemUpdate) -> models.StudyItem:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                try:
                    setattr(db_obj, field, update_data[field])
                except Exception as e:
                    # Attributes data wil he handles on ite own
                    pass
        # reset relationship mode linkages
        obj_in_data = jsonable_encoder(obj_in)
        db_obj.instrument = db_session.query(models.Instrument).get(obj_in_data["instrument_uid"])
        db_obj.style = db_session.query(models.Style).get(obj_in_data["style_uid"])
        ##
        db_obj.attributes.clear()
        for _attr in obj_in_data['attributes']:
            attr = db_session.query(models.Attribute).get(_attr["uid"])
            if not attr in obj_data['attributes']:
                db_obj.attributes.append(attr)
        ##
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj


studyitem = CRUDStudyItem(models.StudyItem)


class CRUDAttribute(CRUDMIXIN[models.Attribute, schemas.AttributeCreate, schemas.AttributeUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[models.Attribute]:
        result = db_session.query(models.Attribute).filter(models.Attribute.name == name).first()
        return result

    def get_multi_by_study(self, db_session: Session, *, study_uid: int, skip=0, limit=100) -> List[models.Attribute]:
        return db_session.query(self.model).filter(models.Attribute.study_uid == study_uid).offset(skip).limit(
            limit).all()


attribute = CRUDAttribute(models.Attribute)

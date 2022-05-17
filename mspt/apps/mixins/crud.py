from typing import List, Optional, Generic, TypeVar, Type, Any, Dict

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from mspt.settings.database import DBModel
from mspt.settings.database.sqlalchemy_filters import apply_pagination
from mspt.settings.database.sqlalchemy_filters import apply_filters
from mspt.settings.database.sqlalchemy_filters import apply_sort

ModelType = TypeVar("ModelType", bound=DBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def _maintain_url_params(shared: bool, sort_on: str, sort_order: str):
    return f"&shared={shared}&sort_on={sort_on}&sort_order={sort_order}"


class CRUDMIXIN(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db_session: Session, uid: int) -> Optional[ModelType]:
        return db_session.query(self.model).filter(self.model.uid == uid).first()

    def get_for_user(self, db_session: Session, uid: int, owner_uid: int) -> Optional[ModelType]:
        return db_session.query(self.model).filter(self.model.uid == uid, self.model.owner_uid == owner_uid).first()

    def get_multi(self, db_session: Session, *, skip=0, limit=100) -> List[ModelType]:
        return db_session.query(self.model).offset(skip).limit(limit).all()

    def get_multi_for_user(self, db_session: Session, *, owner_uid: int, skip=0, limit=100) -> List[ModelType]:
        return db_session.query(self.model).filter(self.model.owner_uid == owner_uid).offset(skip).limit(limit).all()

    def get_multi_shared(self, db_session: Session, *, public: bool, skip=0, limit=100) -> List[ModelType]:
        return db_session.query(self.model).filter(self.model.public == public).offset(skip).limit(limit).all()

    def get_paginated_multi(self, db_session: Session, *, request, page=1, size=10, shared=False, owner_uid=None,
                            sort_on='uid', sort_order='asc', other_filters=None) -> Dict[str, Any]:
        extra_params = _maintain_url_params(shared=shared, sort_on=sort_on, sort_order=sort_order)
        qry = db_session.query(self.model)

        # filter
        filter_spec = []

        # if shared: get shared irregardless of owner uid: get everything shared
        if shared:
            filter_spec.append({'field': 'public', 'op': '==', 'value': shared})

        # else: get for user whether shared or not
        if not shared and owner_uid:
            filter_spec.append({'field': 'owner_uid', 'op': '==', 'value': owner_uid})

        if other_filters:  # [{'field': 'xxxxx', 'op': '==', 'value': 'xxx}]
            for filter in other_filters:
                filter_spec.append(filter)

        qry = apply_filters(qry, filter_spec)

        # sort
        sort_spec = [{'field': sort_on, 'direction': sort_order}]
        qry = apply_sort(qry, sort_spec)

        # Paginate        
        paginated = apply_pagination(qry, page_number=page, page_size=size, request=request)

        paginated['items'] = paginated['items'].all()  # query

        prev_url = paginated['prev_url']
        next_url = paginated['next_url']
        paginated['prev_url'] = f"{prev_url}{extra_params}" if prev_url else None
        paginated['next_url'] = f"{next_url}{extra_params}" if next_url else None

        return paginated

    def create(self, db_session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def update(
        self, db_session: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def remove(self, db_session: Session, *, uid: int) -> ModelType:
        obj = db_session.query(self.model).get(uid)
        db_session.delete(obj)
        db_session.commit()
        return obj

from typing import Any, Dict, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import UUID

from mspt.settings.database import SessionScoped
from mspt.settings.database.mixins import AllFeaturesMixin

InDBSchemaType = TypeVar("InDBSchemaType", bound=PydanticBaseModel)


# noinspection PyPep8Naming
class classproperty(object):
    """
    @property for @classmethod
    taken from http://stackoverflow.com/a/13624858
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


# Enhanced Base Model Class with some django-like super powers
@as_declarative()
class DBModel(AllFeaturesMixin):
    __name__: str
    __abstract__ = True
    
    uid = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    # uid = Column(UUID(), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def all_by_page(cls, page: int = 1, limit: int = 20, **kwargs) -> Dict:
        start = (page - 1) * limit
        end = start + limit
        return cls.query.slice(start, end).all()

    @classmethod
    def get(cls, **kwargs):
        """Return the the first value in database based on given args.
        Example:
            User.get(id=5)
        """
        return cls.where(**kwargs).first()

    @classmethod
    def get_for_user(cls, uid: int, owner_uid: int) -> Optional[ModelType]:
        return cls.get(uid=uid, owner_uid=owner_uid)

    @classmethod
    def get_multi(cls, skip=0, limit=100) -> List[ModelType]:
        return cls.query.offset(skip).limit(limit).all()

    @classmethod
    def get_multi_for_user(cls, owner_uid: int, skip=0, limit=100) -> List[ModelType]:
        return cls.where(owner_uid=owner_uid).offset(skip).limit(limit).all()

    @classmethod
    def get_multi_shared(cls, public: bool, skip=0, limit=100) -> List[ModelType]:
        return cls.where(public=public).offset(skip).limit(limit).all()

    @classmethod
    def get_paginated_multi(cls, request, page=1, size=10, shared=False, owner_uid=None,
                            sort_on='uid', sort_order='asc', other_filters=None) -> Dict[str, Any]:
        extra_params = _maintain_url_params(shared=shared, sort_on=sort_on, sort_order=sort_order)
        qry = cls.query

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

    @classmethod
    def _import(cls, schema_in: InDBSchemaType):
        """Convert Pydantic schema to dict"""
        if isinstance(schema_in, dict):
            return schema_in
        data = schema_in.dict(exclude_unset=True)
        return data

    def save(self):
        """Saves the updated model to the current entity db.
        """
        self.session.add(self)
        self.session.flush()
        self.session.commit()
        return self
    
    @classmethod
    def get_one(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()
    
    def psql_records_to_dict(self, records, many=False):
        # records._row: asyncpg.Record / databases.backends.postgres.Record
        if not many and records:
            return dict(records)
        return [dict(record) for record in records]
    
    @classmethod
    def scalar(cls, filters):
        cls.query.scalar()

    # def get_multi(cls, *, skip: int = 0, limit: int = 100):
    #     return cls.objects.offset(skip).limit(limit).all()
    
DBModel.query = SessionScoped.query_property()
DBModel.set_session(SessionScoped())
from typing import Optional
from sqlalchemy.orm import Session

from mspt.entities.user import User
from mspt.models.user import UserCreate, UserUpdate

from mspt.apps.users import models
from mspt.settings.security import verify_password, get_password_hash


class UserRepository(User):
    @classmethod
    def create(cls, obj_in: UserCreate) -> User:
        data = cls._import(obj_in)
        data['hashed_password'] = get_password_hash(obj_in.password)
        del data['password']
        return super().create(**data)
    
    def update(self, obj_in: UserUpdate) -> User:
        data = self._import(obj_in)
        return super().update(**data)
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.get(email=email)

    def authenticate(self, email: str, password: str) -> Optional[models.User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def is_active(user: models.User) -> bool:
        return user.is_active

    @staticmethod
    def is_superuser(user: models.User) -> bool:
        return user.is_superuser


user_repository = UserRepository()

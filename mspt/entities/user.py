from sqlalchemy import Boolean, Column, String

from mspt.settings.database import DBModel


class User(DBModel):
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    def get_stategies(self):
        """back ref field"""
        return self.strategies

    def get_trades(self):
        """back ref field"""
        return self.trades

    def get_trading_plans(self):
        """back ref field"""
        return self.trading_plans

    def get_studies(self):
        """back ref field"""
        return self.studies

    def get_tasks(self):
        """back ref field"""
        return self.tasks

    def get_instruments(self):
        """back ref field"""
        return self.instruments

    def get_watch_lists(self):
        """back ref field"""
        return self.watch_lists

    def get_styles(self):
        """back ref field"""
        return self.styles

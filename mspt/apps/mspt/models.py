from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Float,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from mspt.apps.users.models import User
from mspt.settings.database import DBModel


class BaseModel(DBModel):
    __abstract__ = True
    name = Column(String)
    description = Column(Text)


class BaseImage(DBModel):
    """Includes Cloudinary Fields"""
    __abstract__ = True
    # image = Column(LargeBinary)
    location = Column(String)
    alt = Column(String(128))
    public_uid = Column(String)
    asset_uid = Column(String)
    signature = Column(String)
    version = Column(String)
    version_uid = Column(String)


class StrategyImage(BaseImage):
    strategy_uid = Column(Integer, ForeignKey("strategy.uid", ondelete="CASCADE"), nullable=False)
    strategy = relationship("Strategy", backref="images")

    def get_ordering_queryset(self):
        return self.strategy.images.all

    def __str__(self) -> str:
        return self.strategy.name + " <image alt:> " + self.alt


class TradeImage(BaseImage):
    trade_uid = Column(Integer, ForeignKey("trade.uid", ondelete="CASCADE"), nullable=False)
    trade = relationship("Trade", backref="images")

    def get_ordering_queryset(self):
        return self.trade.images.all

    def __str__(self) -> str:
        return self.trade.name + " <image alt:> " + self.alt


class Instrument(BaseModel):
    # trades = relationship("Trade", back_populates="instrument")    
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="instruments")
    public = Column(Boolean(), default=False)


class Strategy(BaseModel):
    # images = relationship("StrategyImage")
    # trades = relationship("Trade", back_populates="strategy")    
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="strategies")
    public = Column(Boolean(), default=False)


class Style(BaseModel):
    # trades = relationship("Trade", back_populates="style")    
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=True)
    owner = relationship(User, backref="styles")
    public = Column(Boolean(), default=False)


class Trade(DBModel):
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="trades")
    date = Column(DateTime)
    instrument_uid = Column(Integer, ForeignKey("instrument.uid", ondelete="RESTRICT"), nullable=False)
    instrument = relationship("Instrument", backref="trades", lazy="joined")
    strategy_uid = Column(Integer, ForeignKey("strategy.uid", ondelete="RESTRICT"), nullable=False)
    strategy = relationship("Strategy", backref="trades", lazy="joined")
    position = Column(Boolean(), default=True)  # True == Long Trade, False == Short Trade
    outcome = Column(Boolean(), default=False)  # True == Protibale Trade, False == Losing Trade
    status = Column(Boolean(), default=False)  # True == Running / Open Trade, False == Closed Trade
    pips = Column(Integer)
    rr = Column(Float)
    style_uid = Column(Integer, ForeignKey("style.uid", ondelete="RESTRICT"), nullable=False)
    style = relationship("Style", backref="trades", lazy="joined")
    description = Column(String)
    # images = relationship("TradeImage", back_populates="image")
    sl = Column(Integer)  # Slop loss initial
    tp = Column(Integer)  # TP loss initial
    tp_reached = Column(Boolean(), default=False)  # Duid trade hit targeted tp
    tp_exceeded = Column(Boolean(), default=False)  # Duid trade run beyond targeted tp
    full_stop = Column(Boolean(), default=False)  # Duid trade hit full stop on a loss
    entry_price = Column(Float)
    sl_price = Column(Float)  # initial
    tp_price = Column(Float)  # initial
    scaled_in = Column(Boolean(), default=False)  # Added to existing positions
    scaled_out = Column(Boolean(), default=False)  # Duid you pay the trader
    # Are you opening a position on a instrument that is correlated  \
    # to another instrument with an open postion too?
    correlated_position = Column(Boolean(), default=False)
    public = Column(Boolean(), default=False)


class TradingPlan(BaseModel):
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="trading_plans")
    public = Column(Boolean(), default=False)


class Task(BaseModel):  # or Notes same same    
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="tasks")
    public = Column(Boolean(), default=False)


class StudyItemAttribute(DBModel):
    """ManyToManyField linkage between StudyItem and Attribute"""
    studyitem_uid = Column(Integer, ForeignKey("studyitem.uid"), primary_key=True)
    attribute_uid = Column(Integer, ForeignKey("attribute.uid"), primary_key=True)


class Study(BaseModel):
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="studies")
    public = Column(Boolean(), default=False)


class StudyItemImage(BaseImage):
    studyitem_uid = Column(Integer, ForeignKey("studyitem.uid", ondelete="CASCADE"), nullable=False)
    studyitem = relationship("StudyItem", backref="images", lazy="joined")

    def get_ordering_queryset(self):
        return self.studyitem.images.all

    def __str__(self) -> str:
        return self.studyitem.name + " <image alt:> " + self.alt


class StudyItem(BaseModel):
    study_uid = Column(Integer, ForeignKey("study.uid", ondelete="RESTRICT"), nullable=False)
    study = relationship("Study", backref="studyitems", lazy="joined")
    instrument_uid = Column(Integer, ForeignKey("instrument.uid", ondelete="RESTRICT"), nullable=True)
    instrument = relationship("Instrument", backref="studyitems", lazy="joined")
    position = Column(Boolean(), default=True)  # True == Long Trade, False == Short Trade
    outcome = Column(Boolean(), default=False)  # True == Pfotibale Trade, False == Losing Trade
    pips = Column(Integer)
    rrr = Column(Float)
    style_uid = Column(Integer, ForeignKey("style.uid", ondelete="RESTRICT"), nullable=True)
    style = relationship("Style", backref="studyitems", lazy="joined")
    date = Column(DateTime)
    attributes = relationship("Attribute", secondary=lambda: StudyItemAttribute.__table__, lazy="joined")
    public = Column(Boolean(), default=False)


class Attribute(BaseModel):
    """Additional Features being studied:
    E.g Study: OrderBlock
    Attributes: W1 OB, D1 OB, OB MT, OB Open/Close, OB Low/High
    Study: One SMA
    Attributes: H1/D1 Config, H4/W1 Config"""
    study_uid = Column(Integer, ForeignKey("study.uid", ondelete="RESTRICT"), nullable=False)
    study = relationship("Study", backref="attributes", lazy="joined")
    studyitems = relationship("StudyItem", secondary=lambda: StudyItemAttribute.__table__, lazy="joined")
    public = Column(Boolean(), default=False)


class WatchList(BaseModel):
    owner_uid = Column(Integer, ForeignKey("user.uid", ondelete="CASCADE"), nullable=False)
    owner = relationship(User, backref="watch_lists")
    public = Column(Boolean(), default=False)

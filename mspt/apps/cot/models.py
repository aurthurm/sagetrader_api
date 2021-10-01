
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Float,
    DateTime,
    Integer
)
from sqlalchemy.orm import relationship
from datetime import datetime
from mspt.settings.database import DBModel



class CFTCContract(DBModel):
    """CFTC Contact"""
    name = Column(String(50))
    code = Column(String(20))

    def __str__(self) -> str:
        return f"<CFTC Contact: {self.name} {self.code}>"



class CFTCReport(DBModel):
    contract_uid = Column(Integer, ForeignKey("cftccontract.uid", ondelete="CASCADE"), nullable=False)
    contract = relationship("CFTCContract", backref="reports")
    # "Date"
    date = Column(DateTime)
    # "Open Interest"
    open_interest = Column(Float)
    open_interest_ch = Column(Float)
    # "Noncommercial Long"
    non_commercial_long = Column(Float)
    non_commercial_long_ch = Column(Float)
    # "Noncommercial Short"
    non_commercial_short = Column(Float)
    non_commercial_short_ch = Column(Float)
    # "Noncommercial Spreads"
    non_commercial_spreads = Column(Float)
    non_commercial_spreads_ch = Column(Float)
    # "Commercial Long"
    commercial_long = Column(Float)
    commercial_long_ch = Column(Float)
    # "Commercial Short"
    commercial_short = Column(Float)
    commercial_short_ch = Column(Float)
    # "Total Long"
    total_long = Column(Float)
    total_long_ch = Column(Float)
    # "Total Short"
    total_short = Column(Float)
    total_short_ch = Column(Float)
    # "Nonreportable Positions Long"
    non_reportable_long = Column(Float)
    non_reportable_long_ch = Column(Float)
    # "Nonreportable Positions Short"
    non_reportable_short = Column(Float)
    non_reportable_short_ch = Column(Float)

    def __str__(self) -> str:
        return f"<CFTC Report for : {self.contract.name} dated {self.date}>"
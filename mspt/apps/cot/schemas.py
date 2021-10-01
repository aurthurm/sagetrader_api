from typing import Optional, List, ForwardRef, Any
from datetime import datetime
from pydantic import BaseModel


class BasePaginated(BaseModel):
    count: int
    page: int
    pages: int
    size: int
    next_url: Optional[str] = None
    prev_url: Optional[str] = None


#
# ............................................ CFTCContract Schemas
#
class CFTCContractBase(BaseModel):
    name: str
    code: str
    

class CFTCContractInDBBase(CFTCContractBase):
    uid: int

    class Config:
        orm_mode = True
        
class CFTCContract(CFTCContractInDBBase):
    pass

class CFTCContractUpdate(CFTCContract):
    name: Optional[str] = None
    code: Optional[str] = None

class CFTCContractCreate(CFTCContractBase):
    pass

class CFTCContractDelete(CFTCContractInDBBase):
    pass
    


#
# ............................................ CFTCReport Schemas
#
class CFTCReportBase(BaseModel):
    contract_uid: str
    date: datetime
    open_interest: float
    open_interest_ch: float
    non_commercial_long: float
    non_commercial_long_ch: float
    non_commercial_short: float
    non_commercial_short_ch: float
    non_commercial_spreads: float
    non_commercial_spreads_ch: float
    commercial_long: float
    commercial_long_ch: float
    commercial_short: float
    commercial_short_ch: float
    total_long: float
    total_long_ch: float
    total_short: float
    total_short_ch: float
    non_reportable_long: float
    non_reportable_long_ch: float
    non_reportable_short: float
    non_reportable_short_ch: float

class CFTCReportInDBBase(CFTCReportBase):
    uid: int

    class Config:
        orm_mode = True
        
class CFTCReport(CFTCReportInDBBase):
    contract: Optional[CFTCContract]

class CFTCReportUpdate(CFTCReport):
    contract: Optional[CFTCContract] = None

class CFTCReportCreate(CFTCReportBase):
    pass

class CFTCReportDelete(CFTCReportInDBBase):
    pass


class CFTCReportPaginated(BasePaginated):
    items: List[CFTCReport]

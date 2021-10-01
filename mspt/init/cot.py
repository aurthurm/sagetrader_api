import logging, coloredlogs

from mspt.settings import config
from mspt.apps.cot import schemas, crud, utils

coloredlogs.install()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

    
contracts = [
    schemas.CFTCContractCreate(name="USDX", code="098662"),
    schemas.CFTCContractCreate(name="EUR", code="099741"),
    schemas.CFTCContractCreate(name="GBP", code="096742"),
    schemas.CFTCContractCreate(name="CAD", code="090741"),
    schemas.CFTCContractCreate(name="AUD", code="232741"),
    schemas.CFTCContractCreate(name="NZD", code="112741"),
    schemas.CFTCContractCreate(name="CHF", code="092741"),
    schemas.CFTCContractCreate(name="ZAR", code="122741"),
    schemas.CFTCContractCreate(name="JPY", code="097741"),
    schemas.CFTCContractCreate(name="GOLD", code="088691"),
    schemas.CFTCContractCreate(name="DOW", code="124603"),
    schemas.CFTCContractCreate(name="SP500 EMINI", code="13874A"),
    schemas.CFTCContractCreate(name="NASDAQ MINI", code="209742"),
    schemas.CFTCContractCreate(name="US Treasury Bonds", code="020601"),
    schemas.CFTCContractCreate(name="2 Yr TNote", code="042601"),
    schemas.CFTCContractCreate(name="5 Yr TNote", code="044601"),
    schemas.CFTCContractCreate(name="10 Yr TNote", code="043602"),
]

def initialise_cot(db_session):
    
    db_cntrcts = crud.ctfc_contract.get_multi(db_session=db_session)
        
    logger.info("Initializing COT Data Contracts")
    for cot_in in contracts:
        cot = crud.ctfc_contract.get_by_name(db_session=db_session, name=cot_in.name)
        if not cot:
            crud.ctfc_contract.create(db_session=db_session, obj_in=cot_in)
        else:
            logger.info(f" COT Data  exists {cot.name}")
    logger.info(" COT Data  Initialised")
    
    # logger.info("Loading cot data from quandl")
    # db_cntrcts = crud.ctfc_contract.get_multi(db_session=db_session)
    # logger.info(f"Contracts to execute {db_cntrcts}")
    # for ctr in db_cntrcts:
    #     logger.info(f"Fetching {ctr.name} Contract data from quandl ")
    #     data_all, data_ch = utils.get_data(ctr.code)
    #     logger.info(f"persisiting ...")
    #     utils.persist_data(db_session, ctr, data_all, data_ch)

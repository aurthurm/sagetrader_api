from typing import List
import time
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Form,
    Query,
)
from sqlalchemy.orm import Session

from mspt.apps.mspt import (
    schemas,
    crud,
    utils
)
from mspt.apps.users import models as user_models
from mspt.settings.database import get_db
from mspt.settings.security import (
    get_current_active_user
)
from mspt.utils.create_dirs import resolve_media_dirs_for

router = APIRouter()
db_session = Session()


#
# ........ Image Uploads Handler .........
#
@router.post("/uploads-handler")
async def handle_file_uploads(
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(...),
    parent: str = Form(...),
    tags: str = Form(...),
    caption: str = Form(...)
):
    parent, parent_uid = parent.split('-')
    media_dir = resolve_media_dirs_for(parent)
    images = []

    for _file in files:
        file_path = media_dir + _file.filename
        resp = await utils.save_or_upload(
            file_path=file_path,
            img_file=_file,
            tags=tags,
            caption=caption,
            parent=parent,
            parent_uid=parent_uid,
        )
        utils.persist_image_metadata(
            db=db,
            parent=parent,
            parent_uid=parent_uid,
            location=resp.get('url', None),
            public_uid=resp.get('public_uid', None),
            asset_uid=resp.get('asset_uid', None),
            signature=resp.get('signature', None),
            version=resp.get('version', None),
            version_uid=resp.get('version_uid', None)
        )
        images = utils.get_image_response(db=db, parent=parent, parent_uid=parent_uid)
    return images


@router.get("/fetch-files/{parent_uidentifier}")
async def fetch_files(
    *,
    db: Session = Depends(get_db),
    parent_uidentifier: str
):
    parent, parent_uid = parent_uidentifier.split('-')
    resolve_media_dirs_for(parent)
    images = utils.get_image_response(db=db, parent=parent, parent_uid=parent_uid)
    return images


@router.delete("/delete-file/{uidentifier}")
async def delete_files(
    *,
    db: Session = Depends(get_db),
    uidentifier: str
):
    parent, file_uid = uidentifier.split('-')
    response = utils.delete_images(db=db, parent=parent, file_uid=file_uid)
    return response


#
# ........ Instrument Routes .........
#
@router.get("/instrument", response_model=List[schemas.Instrument])
def read_instruments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve instruments.
    """
    instruments = crud.instrument.get_multi_for_user(db, owner_uid=current_user.uid, skip=skip, limit=limit)
    return instruments


@router.post("/instrument", response_model=schemas.Instrument)
def create_instrument(
    *,
    db: Session = Depends(get_db),
    instrument_in: schemas.InstrumentCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new instrument.
    """

    instrument = crud.instrument.get_by_name_owner(db, name=instrument_in.name, owner_uid=current_user.uid)
    if instrument:
        raise HTTPException(
            status_code=400,
            detail="This instrument already exists in the system.",
        )
    instrument_in.name = instrument_in.name.upper()
    instrument_in.owner_uid = current_user.uid
    instrument = crud.instrument.create(db, obj_in=instrument_in)
    return instrument


@router.put("/instrument/{instrument_uid}", response_model=schemas.Instrument)
def update_instrument(
    *,
    db: Session = Depends(get_db),
    instrument_uid: int,
    instrument_in: schemas.InstrumentUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an instrument.
    """
    instrument = crud.instrument.get(db, uid=instrument_uid)
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail="This instrument does not exist in the system",
        )
    instrument = crud.instrument.update(db, db_obj=instrument, obj_in=instrument_in)
    return instrument


@router.delete("/instrument/{instrument_uid}", response_model=schemas.InstrumentDelete)
def delete_instrument(
    *,
    db: Session = Depends(get_db),
    instrument_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an instrument.
    """
    instrument = crud.instrument.get(db, uid=instrument_uid)
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail="This instrument does not exist in the system",
        )
    instrument = crud.instrument.remove(db, uid=instrument_uid)
    return instrument


#
# ........ Style Routes .........
#
@router.get("/style", response_model=List[schemas.Style])
def read_styles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve styles.
    """
    styles = crud.style.get_multi(db, skip=skip, limit=limit)
    return styles


@router.post("/style", response_model=schemas.Style)
def create_style(
    *,
    db: Session = Depends(get_db),
    style_in: schemas.StyleCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new style.
    """
    style = crud.style.get_by_name(db, name=style_in.name)
    if style:
        raise HTTPException(
            status_code=400,
            detail="This style already exists in the system.",
        )
    style_in.owner_uid = None
    style = crud.style.create(db, obj_in=style_in)
    return style


@router.put("/style/{style_uid}", response_model=schemas.Style)
def update_style(
    *,
    db: Session = Depends(get_db),
    style_uid: int,
    style_in: schemas.StyleUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an style.
    """
    style = crud.style.get(db, uid=style_uid)
    if not style:
        raise HTTPException(
            status_code=404,
            detail="This style does not exist in the system",
        )
    style = crud.style.update(db, db_obj=style, obj_in=style_in)
    return style


@router.delete("/style/{style_uid}", response_model=schemas.StyleDelete)
def delete_style(
    *,
    db: Session = Depends(get_db),
    style_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an style.
    """
    style = crud.style.get(db, uid=style_uid)
    if not style:
        raise HTTPException(
            status_code=404,
            detail="This style does not exist in the system",
        )
    style = crud.style.remove(db, uid=style_uid)
    return style


#
# ........ Strategy Routes .........
#
@router.get("/strategy", response_model=List[schemas.StrategyPlusStats])  # List[schemas.Strategy]
def read_strategies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    shared: bool = Query(False),
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve strategies.
    """

    if not shared:
        strategies = crud.strategy.get_multi_for_user(db, owner_uid=current_user.uid, skip=skip, limit=limit)
    else:
        strategies = crud.strategy.get_multi_shared(db, public=shared, skip=skip, limit=limit)

    # Get strategy stats
    _strategies: list = []
    _strategy: dict = {}
    for strategy in strategies:
        won: int = 0
        total_trades: int = len(strategy.trades)
        for trade in strategy.trades:
            if trade.outcome:
                won += 1
        lost: int = total_trades - won
        if total_trades != 0:
            win_rate = (won / total_trades) * 100
        else:
            win_rate = 0

        # Build strategy obj and push
        _strategy = {
            'uid': strategy.uid,
            'name': strategy.name,
            'owner_uid': strategy.owner_uid,
            'owner': strategy.owner,
            'description': strategy.description,
            'total_trades': total_trades,
            'won_trades': won,
            'lost_trades': lost,
            'public': strategy.public,
        }
        _strategies.append(_strategy)
    return _strategies


@router.post("/strategy", response_model=schemas.StrategyPlusStats)
def create_strategy(
    *,
    db: Session = Depends(get_db),
    strategy_in: schemas.StrategyCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new strategy.
    """
    strategy = crud.strategy.get_by_name_owner(db, name=strategy_in.name, owner_uid=current_user.uid)
    if strategy:
        raise HTTPException(
            status_code=400,
            detail="This strategy already exists in the system.",
        )
    strategy_in.owner_uid = current_user.uid
    strategy = crud.strategy.create(db, obj_in=strategy_in)
    #  stats
    won: int = 0
    total_trades: int = len(strategy.trades)
    for trade in strategy.trades:
        if trade.outcome:
            won += 1
    lost: int = total_trades - won
    if total_trades != 0:
        win_rate = (won / total_trades) * 100
    else:
        win_rate = 0

    # Build strategy obj and push
    _strategy = {
        'uid': strategy.uid,
        'name': strategy.name,
        'owner_uid': strategy.owner_uid,
        'owner': strategy.owner,
        'description': strategy.description,
        'total_trades': total_trades,
        'won_trades': won,
        'lost_trades': lost,
        'win_rate': win_rate,
        'public': strategy.public,
    }
    return _strategy


@router.put("/strategy/{strategy_uid}", response_model=schemas.StrategyPlusStats)
def update_strategy(
    *,
    db: Session = Depends(get_db),
    strategy_uid: int,
    strategy_in: schemas.StrategyUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an strategy.
    """
    strategy = crud.strategy.get(db, uid=strategy_uid)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="This strategy does not exist in the system",
        )
    strategy = crud.strategy.update(db, db_obj=strategy, obj_in=strategy_in)
    #  stats
    won: int = 0
    total_trades: int = len(strategy.trades)
    for trade in strategy.trades:
        if trade.outcome:
            won += 1
    lost: int = total_trades - won
    if total_trades != 0:
        win_rate = (won / total_trades) * 100
    else:
        win_rate = 0

    # Build strategy obj and push
    _strategy = {
        'uid': strategy.uid,
        'name': strategy.name,
        'description': strategy.description,
        'owner_uid': strategy.owner_uid,
        'owner': strategy.owner,
        'total_trades': total_trades,
        'won_trades': won,
        'lost_trades': lost,
        'win_rate': win_rate,
        'public': strategy.public,
    }
    return _strategy


@router.delete("/strategy/{strategy_uid}", response_model=schemas.StrategyDelete)
def delete_strategy(
    *,
    db: Session = Depends(get_db),
    strategy_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an strategy.
    """
    strategy = crud.strategy.get(db, uid=strategy_uid)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="This style does not exist in the system",
        )
    strategy = crud.strategy.remove(db, uid=strategy_uid)
    return strategy


#
# ........ Trade Routes .........
#

@router.get("/trade", response_model=List[schemas.Trade])
def read_trades(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    shared: bool = Query(False),
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve trades.
    """
    if not shared:
        trades = crud.trade.get_multi_for_user(db, owner_uid=current_user.uid, skip=skip, limit=limit)
    else:
        trades = crud.trade.get_multi_shared(db, public=shared, skip=skip, limit=limit)

    for trade in trades:
        trade.date = str(trade.date)
    return trades


@router.post("/trade", response_model=schemas.Trade)
def create_trade(
    *,
    db: Session = Depends(get_db),
    trade_in: schemas.TradeCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new trade.
    """
    trade_in.owner_uid = current_user.uid
    trade = crud.trade.create(db, obj_in=trade_in)
    trade.date = str(trade.date)
    return trade


@router.put("/trade/{trade_uid}", response_model=schemas.Trade)
def update_trade(
    *,
    db: Session = Depends(get_db),
    trade_uid: int,
    trade_in: schemas.TradeUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an trade.
    """
    trade = crud.trade.get(db, uid=trade_uid)
    if not trade:
        raise HTTPException(
            status_code=404,
            detail="This trade does not exist in the system",
        )
    trade = crud.trade.update(db, db_obj=trade, obj_in=trade_in)
    trade.date = str(trade.date)
    return trade


@router.delete("/trade/{trade_uid}", response_model=schemas.TradeDelete)
def delete_trade(
    *,
    db: Session = Depends(get_db),
    trade_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an trade.
    """
    trade = crud.trade.get(db, uid=trade_uid)
    if not trade:
        raise HTTPException(
            status_code=404,
            detail="This trade does not exist in the system",
        )
    trade = crud.trade.remove(db, uid=trade_uid)
    trade.date = str(trade.date)
    return trade


#
# ........ TradingPlan Routes .........
#

@router.get("/trading-plan", response_model=List[schemas.TradingPlan])
def read_trading_plans(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    shared: bool = Query(False),
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve trading plans.
    """
    if not shared:
        trading_plans = crud.trading_plan.get_multi_for_user(db, owner_uid=current_user.uid, skip=skip, limit=limit)
    else:
        trading_plans = crud.trading_plan.get_multi_shared(db, public=shared, skip=skip, limit=limit)
    return trading_plans


@router.post("/trading-plan", response_model=schemas.TradingPlan)
def create_trading_plan(
    *,
    db: Session = Depends(get_db),
    plan_in: schemas.TradingPlanCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new trading plan.
    """
    t_plan = crud.trading_plan.get_by_name_owner(db, name=plan_in.name, owner_uid=current_user.uid)
    if t_plan:
        raise HTTPException(
            status_code=400,
            detail="A trading plan with this name already exists",
        )
    plan_in.owner_uid = current_user.uid
    trading_plan = crud.trading_plan.create(db, obj_in=plan_in)
    return trading_plan


@router.put("/trading-plan/{plan_uid}", response_model=schemas.TradingPlan)
def update_trading_plan(
    *,
    db: Session = Depends(get_db),
    plan_uid: int,
    plan_in: schemas.TradingPlanUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an trading_plan.
    """
    trading_plan = crud.trading_plan.get(db, uid=plan_uid)
    if not trading_plan:
        raise HTTPException(
            status_code=404,
            detail="This trading_plan does not exist in the system",
        )
    trading_plan = crud.trading_plan.update(db, db_obj=trading_plan, obj_in=plan_in)
    return trading_plan


@router.delete("/trading-plan/{plan_uid}", response_model=schemas.TradingPlanDelete)
def delete_trading_plan(
    *,
    db: Session = Depends(get_db),
    plan_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an trading_plan.
    """
    trading_plan = crud.trading_plan.get(db, uid=plan_uid)
    if not trading_plan:
        raise HTTPException(
            status_code=404,
            detail="This trading_plan does not exist in the system",
        )
    trading_plan = crud.trading_plan.remove(db, uid=plan_uid)
    return trading_plan


#
# ........ Task Routes .........
#

@router.get("/task", response_model=List[schemas.Task])
def read_task(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve tasks.
    """
    # tasks = crud.task.get_multi_for_user(db, owner_uid=current_user.uid, skip=skip, limit=limit)
    tasks = current_user.get_tasks()
    return tasks


@router.post("/task", response_model=schemas.Task)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: schemas.TaskCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new task.
    """
    task_in.owner_uid = current_user.uid
    task = crud.task.create(db, obj_in=task_in)
    return task


@router.put("/task/{task_uid}", response_model=schemas.Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    task_uid: int,
    task_in: schemas.TaskUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an task.
    """
    task = crud.task.get(db, uid=task_uid)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="This task does not exist in the system",
        )
    task = crud.task.update(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/task/{task_uid}", response_model=schemas.TaskDelete)
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an task.
    """
    task = crud.task.get(db, uid=task_uid)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="This task does not exist in the system",
        )
    task = crud.task.remove(db, uid=task_uid)
    return task


#
# ........ Study Routes .........
#

@router.get("/study", response_model=List[schemas.StudyWithAttrs])
def read_study(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    shared: bool = Query(False),
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve studies.
    """
    if not shared:
        studies = crud.study.get_multi_for_user(db, owner_uid=current_user.uid, skip=skip, limit=limit)
    else:
        studies = crud.study.get_multi_shared(db, public=shared, skip=skip, limit=limit)
    return studies


@router.post("/study", response_model=schemas.Study)
def create_study(
    *,
    db: Session = Depends(get_db),
    study_in: schemas.StudyCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new study.
    """
    study_in.owner_uid = current_user.uid
    study = crud.study.create(db, obj_in=study_in)
    return study


@router.put("/study/{study_uid}", response_model=schemas.Study)
def update_study(
    *,
    db: Session = Depends(get_db),
    study_uid: int,
    study_in: schemas.StudyUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an study.
    """
    study = crud.study.get(db, uid=study_uid)
    if not study:
        raise HTTPException(
            status_code=404,
            detail="This study does not exist in the system",
        )
    study = crud.study.update(db, db_obj=study, obj_in=study_in)
    return study


@router.delete("/study/{study_uid}", response_model=schemas.StudyDelete)
def delete_study(
    *,
    db: Session = Depends(get_db),
    study_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an study.
    """
    study = crud.study.get(db, uid=study_uid)
    if not study:
        raise HTTPException(
            status_code=404,
            detail="This study does not exist in the system",
        )
    study = crud.study.remove(db, uid=study_uid)
    return study


#
# ........ Study Item Routes .........
#

@router.get("/studyitems/{study_uid}", response_model=List[schemas.StudyItemWithAttrs])
def read_studyitems(
    *,
    db: Session = Depends(get_db),
    study_uid: int,
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve studyitems.
    """
    studies = crud.studyitem.get_multi_by_study(db, study_uid=study_uid, skip=skip, limit=limit)
    # for study in studies:
    #     study.date = str(study.date)
    return studies


@router.post("/studyitems", response_model=schemas.StudyItemWithAttrs)
def create_studyitems(
    *,
    db: Session = Depends(get_db),
    studyitem_in: schemas.StudyItemCreateWithAttrs,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new studyitem.
    """
    studyitem = crud.studyitem.create(db, obj_in=studyitem_in)
    # studyitem.date = str(studyitem.date)
    return studyitem


@router.put("/studyitems/{studyitem_uid}", response_model=schemas.StudyItemWithAttrs)
def update_studyitems(
    *,
    db: Session = Depends(get_db),
    studyitem_uid: int,
    studyitem_in: schemas.StudyItemUpdateWithAttrs,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an studyitems.
    """
    studyitem = crud.studyitem.get(db, uid=studyitem_uid)
    if not studyitem:
        raise HTTPException(
            status_code=404,
            detail="This studyitem does not exist in the system",
        )

    studyitem = crud.studyitem.update(db, db_obj=studyitem, obj_in=studyitem_in)
    # studyitem.date = str(studyitem.date)
    return studyitem


@router.delete("/studyitems/{studyitem_uid}", response_model=schemas.StudyItem)
def delete_studyitems(
    *,
    db: Session = Depends(get_db),
    studyitem_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an studyitem.
    """
    studyitem = crud.studyitem.get(db, uid=studyitem_uid)
    if not studyitem:
        raise HTTPException(
            status_code=404,
            detail="This studyitem does not exist in the system",
        )
    studyitem = crud.studyitem.remove(db, uid=studyitem_uid)
    return studyitem


#
# ........ Attribute Routes .........
#

@router.get("/attribute/{study_uid}", response_model=List[schemas.Attribute])
def read_attributes(
    *,
    db: Session = Depends(get_db),
    study_uid: int,
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Retrieve Attrs.
    """
    attrs = crud.attribute.get_multi_by_study(db, study_uid=study_uid, skip=skip, limit=limit)
    return attrs


@router.post("/attribute", response_model=schemas.Attribute)
def create_attribute(
    *,
    db: Session = Depends(get_db),
    attrs_in: schemas.AttributeCreate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Create new attr.
    """
    attrs = crud.attribute.create(db, obj_in=attrs_in)
    return attrs


@router.put("/attribute/{attr_uid}", response_model=schemas.Attribute)
def update_attribute(
    *,
    db: Session = Depends(get_db),
    attr_uid: int,
    attr_in: schemas.AttributeUpdate,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Update an attr.
    """
    attr = crud.attribute.get(db, uid=attr_uid)
    if not attr:
        raise HTTPException(
            status_code=404,
            detail="This attribute does not exist in the system",
        )
    attr = crud.attribute.update(db, db_obj=attr, obj_in=attr_in)
    return attr


@router.delete("/attribute/{attr_uid}", response_model=schemas.Attribute)
def delete_attribute(
    *,
    db: Session = Depends(get_db),
    attr_uid: int,
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Delete an attr.
    """
    attr = crud.attribute.get(db, uid=attr_uid)
    if not attr:
        raise HTTPException(
            status_code=404,
            detail="This attribute does not exist in the system",
        )
    attr = crud.attribute.remove(db, uid=attr_uid)
    return attr


#
# ........ Trading Statistics .........
#

@router.get("/peformance-measures")
def trade_stats(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_active_user),
):
    """
    Calculate Trading Statistics.
    """

    # 1. Stategy Win Rates
    # overal peformance
    # by pair
    # by style
    # by position type

    # 2. RiskReward
    # overal peformance
    # by pair
    # by style
    # by strategy

    # 3. Average Pips Lost/Gained
    # overal peformance
    # by pair
    # by strategy
    # by style

    # 3. Intsrument Peformances
    # overal peformance
    # by strategy
    # by style
    # by position type

    # 2. Other Stats

    return {}

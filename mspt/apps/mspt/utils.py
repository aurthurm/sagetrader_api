from typing import Dict, Optional, List, Any

import cloudinary as Cloud
from cloudinary.exceptions import Error as CloudinaryErrorException
from cloudinary.uploader import (
    upload as CloudUploader,
    destroy as CloudDestroy,
)
import io
from PIL import Image

from sqlalchemy.orm import Session
from fastapi import HTTPException

from mspt.utils.create_dirs import deleteFile
from mspt.apps.mspt import models

Cloud.config(
    cloud_name='d3sage',
    api_key='979235147696769',
    api_secret='4QrvbQ_BDUw32ns6WeIf6pABf6U'
)

PRESET_TESTING = 'mspt_testing'
PRESET_PRODUCTION = 'mspt_osok'


# overwrite, use_filename, unique_filename
# upload_preset = 'mspt_testing', # mspt_osok,
# Cloudinary Error Handling Codes

# 200 - OK. Successful.
# 400 - Bad request. Invaluid request parameters.
# 401 - Authorization required.
# 403 - Not allowed.
# 404 - Not found.
# 420 - Rate limited.
# 500 - Internal error. Contact support.
# context alt=My image❘caption=Profile image or ['alt': 'My image', 'caption': 'Profile image']
# metadata = in_stock_uid=50❘color_uid=[\"green\",\"red\"]

def persist_image_metadata(db: Session, parent: str, parent_uid: str, location: str, alt: str = "", **kwargs):
    if parent == "studyitem":
        image_obj = models.StudyItemImage()
        image_obj.studyitem = db.query(models.StudyItem).get(int(parent_uid))
        image_obj.studyitem_uid = int(parent_uid)
    elif parent == "trade":
        image_obj = models.TradeImage()
        image_obj.trade = db.query(models.Trade).get(int(parent_uid))
        image_obj.trade_uid = int(parent_uid)
    elif parent == "strategy":
        image_obj = models.StrategyImage()
        image_obj.strategy = db.query(models.Strategy).get(int(parent_uid))
        image_obj.strategy_uid = int(parent_uid)
    else:
        raise Exception(f"Unknown Parent: {parent}")

    image_obj.alt = alt
    image_obj.location = location
    image_obj.public_uid = kwargs.get('public_uid', None)
    image_obj.asset_uid = kwargs.get('asset_uid', None)
    image_obj.signature = kwargs.get('signature', None)
    image_obj.version = kwargs.get('version', None)
    image_obj.version_uid = kwargs.get('version_uid', None)
    db.add(image_obj)
    db.commit()
    db.refresh(image_obj)


async def save_or_upload(
    file_path: str,
    img_file,
    tags: str,
    caption: str,
    parent: str,
    parent_uid: str,
    save: bool = False
) -> Optional[Dict]:
    await img_file.seek(0)
    image = await img_file.read()
    if save:
        """Save to local disk"""
        _image = Image.open(io.BytesIO(image))
        _image.save(file_path)
        # response = await CloudUploader(file_path,  tags=tags) 

    options = dict()
    options['tags'] = [tag.strip() for tag in tags.split(",")] if tags else []
    options['upload_preset'] = PRESET_PRODUCTION
    options['context'] = f'caption={caption}|alt={tags}'
    options['folder'] = _folder_from_preset(parent, PRESET_PRODUCTION)

    response = None
    try:
        response = CloudUploader(image, **options)
    except CloudinaryErrorException as ce:
        raise HTTPException(
            status_code=424,  # Failed Dependency, 500 Internal server Error, # 503 Service unavailable
            detail=f"Cloudinary Image Backend Error {ce}",
            headers={'X-Error': f"{ce}"}
        )

    return response


def get_image_response(db: Session, parent: str, parent_uid: str) -> List[Any]:
    if parent == "studyitem":
        images = db.query(models.StudyItemImage).filter_by(studyitem_uid=int(parent_uid)).offset(0).limit(100).all()
    elif parent == "trade":
        images = db.query(models.TradeImage).filter_by(trade_uid=int(parent_uid)).offset(0).limit(100).all()
    elif parent == "strategy":
        images = db.query(models.StrategyImage).filter_by(strategy_uid=int(parent_uid)).offset(0).limit(100).all()
    else:
        raise Exception(f"Unknown Parent: {parent}")
    return images


def delete_images(db: Session, parent: str, file_uid: str, local: bool = False):
    obj = None
    if parent == "strategy":
        obj = db.query(models.StrategyImage).get(int(file_uid))
    elif parent == "trade":
        obj = db.query(models.TradeImage).get(int(file_uid))
    elif parent == "studyitem":
        obj = db.query(models.StudyItemImage).get(int(file_uid))

    if local:
        if deleteFile(obj.location):
            db.delete(obj)
            db.commit()

    resp = CloudDestroy(obj.public_uid)
    if resp.get('result', '') == 'ok':
        db.delete(obj)
        db.commit()

    return resp


def _folder_from_preset(parent: str, preset: str):
    _base_folder = ""
    if preset == PRESET_PRODUCTION:
        _base_folder = "mspt"
    else:
        _base_folder = "testing"

    return f"{_base_folder}/{parent}"

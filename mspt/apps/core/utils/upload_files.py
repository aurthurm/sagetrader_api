import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable
import uuid
from fastapi import UploadFile

filename = uuid.uuid4().hex


def save_upload_file(upload_file: UploadFile, destination: Path) -> Dict:
    try:
        upload_file.file.seek(0)
        with destination.open("wb+") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

    return {"filename": upload_file.filename, "path": Path(upload_file.name)}


def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        upload_file.file.seek(0)
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
        # upload_file.filename
    return tmp_path

# Exampe usage
# tmp_path = save_upload_file_tmp(upload_file)
# try: # Do something with the saved temp file
#     pass
# finally:
#     tmp_path.unlink()  # Delete the temp file

# @router.post("/uploads-handler-old")
# def handle_file_uploads_old(files: List[UploadFile] = File(...), for_file: str = Form(...)):
#     general_path = Path('images')
#     trade_path = Path('images/trades')
#     strategy_path = Path('images/strategies')
#     print(f"For File data: {for_file}")
#     for i, _file in enumerate(files):        
#         response = save_upload_file(_file, general_path)
#         # create a model .....
#         print(f"Response {i}: {response}")
#     return {}


# Another thing to consider with linux based OSs is the inode cache, 
# which can grow pretty large as you accumulate files without rebooting, 
# eating an unnecesary amount of RAM. But luckily that's very easy to deal with:

#        sudo sync && sudo echo 10000 | sudo tee /proc/sys/vm/vfs_cache_pressure
#        This instructs the kernel to reclaim cache space more aggresively. Alternatively:

#        sudo sync && sudo echo 3 | sudo tee /proc/sys/vm/drop_caches;
#        This dumps all file system caches, including inodes. More on all of this here.

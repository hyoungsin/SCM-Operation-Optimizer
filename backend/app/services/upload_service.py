import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app.core.config import UPLOAD_DIR
from app.repository.run_repository import create_run
from app.schemas.common import UploadResponse


async def save_upload(file: UploadFile) -> UploadResponse:
    run_id = str(uuid.uuid4())
    upload_time = datetime.now(timezone.utc).isoformat()
    destination = UPLOAD_DIR / f"{run_id}_{Path(file.filename).name}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    create_run(
        run_id=run_id,
        filename=Path(file.filename).name,
        input_path=destination,
        uploaded_at=upload_time,
    )
    return UploadResponse(
        run_id=run_id,
        filename=Path(file.filename).name,
        upload_time=upload_time,
        next_step="validation",
    )

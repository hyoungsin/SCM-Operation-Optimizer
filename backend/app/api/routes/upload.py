from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.common import UploadResponse
from app.services.upload_service import save_upload

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_input(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")
    return await save_upload(file)
